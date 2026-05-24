"""
Mock Bluetooth Transmitter Test
Tests the BLE transmitter functionality without requiring actual BLE hardware.
Simulates a controller sending CAN signal data to a mock client.
"""

import unittest
import threading
import time
from unittest.mock import Mock, MagicMock, patch
from extra.signal_cache import signal_cache


class MockBLETransmitter:
    """Mock BLE transmitter that simulates the real transmitter behavior."""
    
    def __init__(self):
        self.clients = []
        self.running = False
        self.notify_thread = None
        self.update_frequency = 0.2  # 200ms = 5 updates/sec
    
    def add_client(self, client_callback):
        """Register a client to receive notifications."""
        self.clients.append(client_callback)
    
    def notify_all_clients(self):
        """Send latest data to all connected clients."""
        formatted_data = signal_cache.get_formatted_string()
        for client in self.clients:
            client(formatted_data)
    
    def start_notification_loop(self):
        """Start periodic notifications."""
        self.running = True
        def loop():
            while self.running:
                self.notify_all_clients()
                time.sleep(self.update_frequency)
        self.notify_thread = threading.Thread(target=loop, daemon=True)
        self.notify_thread.start()
    
    def stop(self):
        """Stop the transmitter."""
        self.running = False
        if self.notify_thread:
            self.notify_thread.join(timeout=1)


class TestBLETransmitter(unittest.TestCase):
    """Test cases for BLE transmitter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transmitter = MockBLETransmitter()
        self.received_data = []
    
    def mock_client_callback(self, data):
        """Mock client that receives and stores data."""
        self.received_data.append(data)
    
    def tearDown(self):
        """Clean up after tests."""
        self.transmitter.stop()
        self.received_data.clear()
    
    def test_signal_cache_initialization(self):
        """Test that signal cache initializes with all required signals."""
        all_signals = signal_cache.get_all()
        required_signals = ['rpm', 'temp', 'afr', 'tps', 'map', 'battery', 'dwell', 'timing']
        
        for signal in required_signals:
            self.assertIn(signal, all_signals, f"Signal '{signal}' not in cache")
    
    def test_signal_cache_formatted_string(self):
        """Test that signal cache produces correctly formatted output."""
        # Set known values
        signal_cache.update_batch({
            'rpm': 2000,
            'temp': 80.5,
            'afr': 14.25,
            'tps': 25.5,
            'map': 50.0,
            'battery': 12.5,
            'dwell': 5.0,
            'timing': 10.0
        })
        
        formatted = signal_cache.get_formatted_string()
        
        # Should be: rpm,temp,afr,tps,map,battery,dwell,timing
        parts = formatted.split(',')
        self.assertEqual(len(parts), 8, f"Expected 8 fields, got {len(parts)}: {formatted}")
        
        # Verify each part can be parsed as a number
        self.assertEqual(int(parts[0]), 2000)  # rpm
        self.assertAlmostEqual(float(parts[1]), 80.5, places=1)  # temp
        self.assertAlmostEqual(float(parts[2]), 14.25, places=2)  # afr
        self.assertAlmostEqual(float(parts[3]), 25.5, places=1)  # tps
    
    def test_ble_transmitter_notification(self):
        """Test that transmitter sends data to connected clients."""
        self.transmitter.add_client(self.mock_client_callback)
        
        # Set test data
        signal_cache.update_batch({
            'rpm': 3000,
            'temp': 85.0,
            'afr': 13.5,
            'tps': 50.0,
            'map': 75.0,
            'battery': 12.8,
            'dwell': 8.0,
            'timing': 15.0
        })
        
        # Manually trigger notification
        self.transmitter.notify_all_clients()
        
        # Verify data was received
        self.assertEqual(len(self.received_data), 1)
        self.assertIn('3000', self.received_data[0])  # rpm should be present
        self.assertIn('85.0', self.received_data[0])  # temp should be present
    
    def test_continuous_notifications(self):
        """Test that transmitter sends periodic updates."""
        self.transmitter.add_client(self.mock_client_callback)
        self.transmitter.update_frequency = 0.05  # 50ms for faster testing
        
        # Start transmitter
        self.transmitter.start_notification_loop()
        
        # Wait for a few updates
        time.sleep(0.25)
        
        # Should have received at least 4 updates in 250ms (with 50ms frequency)
        self.assertGreaterEqual(len(self.received_data), 4, 
                                f"Expected at least 4 updates, got {len(self.received_data)}")
        
        # All data should be properly formatted
        for data in self.received_data:
            parts = data.split(',')
            self.assertEqual(len(parts), 8, f"Data format incorrect: {data}")
    
    def test_signal_update_propagation(self):
        """Test that signal updates are immediately transmitted."""
        self.transmitter.add_client(self.mock_client_callback)
        
        # Update signals
        signal_cache.update_batch({
            'rpm': 4000,
            'temp': 90.0,
            'afr': 15.0,
            'tps': 75.0,
            'map': 100.0,
            'battery': 13.2,
            'dwell': 10.0,
            'timing': 20.0
        })
        
        # Transmit
        self.transmitter.notify_all_clients()
        
        # Verify the latest values are in the transmission
        received = self.received_data[0]
        parts = received.split(',')
        
        self.assertEqual(int(parts[0]), 4000)  # rpm
        self.assertAlmostEqual(float(parts[1]), 90.0, places=1)  # temp
        self.assertAlmostEqual(float(parts[2]), 15.0, places=2)  # afr
    
    def test_multiple_clients(self):
        """Test that transmitter sends to multiple clients."""
        received_data_1 = []
        received_data_2 = []
        
        def client_1(data):
            received_data_1.append(data)
        
        def client_2(data):
            received_data_2.append(data)
        
        self.transmitter.add_client(client_1)
        self.transmitter.add_client(client_2)
        
        self.transmitter.notify_all_clients()
        
        # Both clients should receive the same data
        self.assertEqual(len(received_data_1), 1)
        self.assertEqual(len(received_data_2), 1)
        self.assertEqual(received_data_1[0], received_data_2[0])
    
    def test_data_format_matches_mobile_app_expectations(self):
        """Test that data format matches what mobile app expects.
        Mobile app parses: rpm,temp,afr,tps,map,battery,dwell,timing
        """
        # Set realistic values
        signal_cache.update_batch({
            'rpm': 2500,
            'temp': 85.5,
            'afr': 14.2,
            'tps': 30.0,
            'map': 65.0,
            'battery': 12.7,
            'dwell': 6.5,
            'timing': 12.5
        })
        
        formatted = signal_cache.get_formatted_string()
        
        # Parse as mobile app would
        parts = formatted.split(',')
        
        rpm = int(parts[0])
        temp = float(parts[1])
        afr = float(parts[2])
        tps = float(parts[3])
        map_val = float(parts[4])
        battery = float(parts[5])
        dwell = float(parts[6])
        timing = float(parts[7])
        
        # Verify values are in expected ranges
        self.assertGreaterEqual(rpm, 1000)
        self.assertLessEqual(rpm, 8000)
        
        self.assertGreaterEqual(temp, 50)
        self.assertLessEqual(temp, 120)
        
        self.assertGreaterEqual(afr, 10)
        self.assertLessEqual(afr, 20)
        
        self.assertGreaterEqual(tps, 0)
        self.assertLessEqual(tps, 100)
    
    def test_notification_frequency(self):
        """Test that notifications occur at the correct frequency (200ms)."""
        self.transmitter.add_client(self.mock_client_callback)
        self.transmitter.update_frequency = 0.05  # 50ms for faster testing
        
        self.transmitter.start_notification_loop()
        
        # Measure time between updates
        start_time = time.time()
        initial_count = 0
        while len(self.received_data) < 3:
            time.sleep(0.01)
        
        elapsed = time.time() - start_time
        
        # Should take roughly 100ms for 2 updates at 50ms frequency
        # Allow 50% tolerance
        expected_time = 0.1  # 2 intervals of 50ms
        self.assertGreater(elapsed, expected_time * 0.5)
        self.assertLess(elapsed, expected_time * 1.5)


class TestIntegrationWithRealTransmitter(unittest.TestCase):
    """Integration tests with the actual BLE transmitter module."""
    
    @patch('transmitter.bluetooth_transmitter.peripheral.Peripheral')
    def test_real_transmitter_initialization(self, mock_peripheral):
        """Test that real transmitter can be initialized without errors."""
        # Mock the peripheral
        mock_instance = MagicMock()
        mock_peripheral.return_value = mock_instance
        
        # Import and test
        from transmitter.bluetooth_transmitter import BLETlmServer
        
        try:
            server = BLETlmServer()
            self.assertIsNotNone(server)
        except Exception as e:
            self.fail(f"BLETlmServer initialization failed: {e}")
    
    def test_signal_cache_thread_safety(self):
        """Test that signal cache is thread-safe."""
        errors = []
        
        def update_thread():
            try:
                for i in range(100):
                    signal_cache.update_batch({
                        'rpm': 2000 + i,
                        'temp': 80 + (i % 20),
                        'afr': 14 + (i % 3),
                        'tps': i % 100,
                        'map': (i * 2) % 300,
                        'battery': 12 + (i % 5),
                        'dwell': i % 180,
                        'timing': (i * 1.5) % 180
                    })
                    signal_cache.get_formatted_string()
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = [threading.Thread(target=update_thread) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")


def run_demo():
    """Run a demonstration of the BLE transmitter."""
    print("\n=== BLE Transmitter Demo ===\n")
    
    transmitter = MockBLETransmitter()
    data_received = []
    
    def demo_client(data):
        data_received.append(data)
        print(f"[CLIENT] Received: {data}")
    
    transmitter.add_client(demo_client)
    
    # Simulate realistic sensor changes
    print("[CONTROLLER] Starting BLE transmitter...")
    transmitter.update_frequency = 0.2  # 200ms
    transmitter.start_notification_loop()
    
    print("[CONTROLLER] Simulating sensor data changes...\n")
    
    sensor_states = {
        'rpm': 2000,
        'temp': 80.0,
        'afr': 14.2,
        'tps': 15.0,
        'map': 50.0,
        'battery': 12.5,
        'dwell': 5.0,
        'timing': 10.0
    }
    
    for step in range(5):
        # Simulate engine revving up
        sensor_states['rpm'] = 2000 + (step * 800)
        sensor_states['temp'] += 1.0
        sensor_states['tps'] = 20 + (step * 15)
        sensor_states['map'] += 10.0
        
        signal_cache.update_batch(sensor_states)
        time.sleep(0.3)
    
    transmitter.stop()
    print(f"\n[SUMMARY] Received {len(data_received)} updates")
    print("[DEMO] Complete!\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        run_demo()
    else:
        unittest.main()
