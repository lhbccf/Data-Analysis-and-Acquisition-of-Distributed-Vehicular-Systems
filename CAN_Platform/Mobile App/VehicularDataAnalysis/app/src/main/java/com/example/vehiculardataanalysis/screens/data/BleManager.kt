package com.example.bleapp.data

import android.Manifest
import android.bluetooth.*
import android.bluetooth.le.*
import android.content.Context
import android.util.Log
import androidx.annotation.RequiresPermission
import com.example.vehiculardataanalysis.domain.Device
import kotlinx.coroutines.flow.MutableStateFlow
import java.util.*

class BleManager(private val context: Context) {

    companion object {
        private const val TAG = "BleManager"

        private val SERVICE_UUID =
            UUID.fromString("12345678-1234-5678-1234-56789abcdef0")

        private val CHAR_UUID =
            UUID.fromString("abcdef01-1234-5678-1234-56789abcdef0")

        private val CCCD_UUID =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
    }

    // 🔄 Flows
    private val _devicesFlow = MutableStateFlow<List<Device>>(emptyList())
    val devicesFlow = _devicesFlow

    private val _dataFlow = MutableStateFlow("")
    val dataFlow = _dataFlow

    private val bluetoothManager =
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager

    private val adapter: BluetoothAdapter = bluetoothManager.adapter
    private val scanner: BluetoothLeScanner = adapter.bluetoothLeScanner

    private var gatt: BluetoothGatt? = null

    // Prevent duplicates - keeps all devices found
    private val foundDevices = mutableMapOf<String, Device>()

    init {
        // Load bonded devices on initialization
        loadBondedDevices()
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    private fun loadBondedDevices() {
        try {
            adapter.bondedDevices.forEach { device ->
                val bleDevice = Device(device.name ?: "Unknown", device.address)
                foundDevices[device.address] = bleDevice
            }
            _devicesFlow.value = foundDevices.values.toList()
            Log.d(TAG, "Loaded ${foundDevices.size} bonded devices")
        } catch (e: Exception) {
            Log.e(TAG, "Error loading bonded devices", e)
        }
    }

    // --------------------------------------------------
    // 🔍 SCAN
    // --------------------------------------------------

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun startScan(adapter: BluetoothAdapter) {
        Log.d(TAG, "Starting BLE scan (preserving ${foundDevices.size} existing devices)")
        scanner.startScan(scanCallback)
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun stopScan() {
        Log.d(TAG, "Stopping BLE scan")
        scanner.stopScan(scanCallback)
    }

    private val scanCallback = object : ScanCallback() {
        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onScanResult(callbackType: Int, result: ScanResult) {

            val device = result.device ?: return

            val name = device.name ?: return
            val address = device.address ?: return

            if (!foundDevices.containsKey(address)) {

                val newDevice = Device(name, address)
                foundDevices[address] = newDevice

                _devicesFlow.value = foundDevices.values.toList()

                Log.d(TAG, "Device found: $name - $address")
            }
        }
    }

    // --------------------------------------------------
    // 🔗 CONNECT
    // --------------------------------------------------

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connect(device: Device) {

        Log.d(TAG, "Connecting to ${device.address}")

        val remoteDevice = adapter.getRemoteDevice(device.address)

        gatt = remoteDevice.connectGatt(
            context,
            false,
            gattCallback
        )
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun disconnect() {
        Log.d(TAG, "Disconnecting")
        gatt?.disconnect()
        gatt?.close()
        gatt = null
    }

    // --------------------------------------------------
    // 📡 GATT CALLBACK
    // --------------------------------------------------

    private val gattCallback = object : BluetoothGattCallback() {

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onConnectionStateChange(
            gatt: BluetoothGatt,
            status: Int,
            newState: Int
        ) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.d(TAG, "Connected → Discovering services")
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.d(TAG, "Disconnected")
            }
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onServicesDiscovered(
            gatt: BluetoothGatt,
            status: Int
        ) {
            Log.d(TAG, "Services discovered")

            val service = gatt.getService(SERVICE_UUID)
            val characteristic = service?.getCharacteristic(CHAR_UUID)

            if (characteristic == null) {
                Log.e(TAG, "Characteristic not found")
                return
            }

            gatt.setCharacteristicNotification(characteristic, true)

            val descriptor = characteristic.getDescriptor(CCCD_UUID)
            if (descriptor != null) {
                descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                gatt.writeDescriptor(descriptor)
            }
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            val value = characteristic.value?.toString(Charsets.UTF_8) ?: ""

            Log.d(TAG, "Data received: $value")

            _dataFlow.value = value
        }
    }

}