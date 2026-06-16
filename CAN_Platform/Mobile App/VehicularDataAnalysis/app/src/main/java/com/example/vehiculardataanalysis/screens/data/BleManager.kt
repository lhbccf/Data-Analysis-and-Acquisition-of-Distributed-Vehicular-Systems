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
        private val SESSION_REQUEST_CHAR_UUID =
            UUID.fromString("abcdef02-1234-5678-1234-56789abcdef0")
        private val SESSION_RESPONSE_CHAR_UUID =
            UUID.fromString("abcdef03-1234-5678-1234-56789abcdef0")
        private val CCCD_UUID =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
    }

    private val _devicesFlow = MutableStateFlow<List<Device>>(emptyList())
    val devicesFlow = _devicesFlow

    private val _dataFlow = MutableStateFlow("")
    val dataFlow = _dataFlow

    private val _sessionFlow = MutableStateFlow("")
    val sessionFlow = _sessionFlow

    private val _connectionReady = MutableStateFlow(false)
    val connectionReady: kotlinx.coroutines.flow.Flow<Boolean> = _connectionReady

    private val bluetoothManager =
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    private val adapter: BluetoothAdapter = bluetoothManager.adapter
    private var scanner: BluetoothLeScanner? = null
    private var gatt: BluetoothGatt? = null
    private val foundDevices = mutableMapOf<String, Device>()

    // Held between onServicesDiscovered and onDescriptorWrite so the two CCCD
    // writes happen sequentially — the stack rejects concurrent descriptor writes.
    private var pendingSessionCharSubscription: BluetoothGattCharacteristic? = null

    init {
        try {
            scanner = adapter.bluetoothLeScanner
        } catch (e: SecurityException) {
            Log.w(TAG, "BluetoothLeScanner initialization deferred (permissions not yet granted)")
        }
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    private fun loadBondedDevices() {
        try {
            adapter.bondedDevices.forEach { device ->
                foundDevices[device.address] = Device(
                    name = device.name ?: "Unknown",
                    address = device.address,
                    isPairedOnly = true
                )
            }
            _devicesFlow.value = foundDevices.values.toList()
            Log.d(TAG, "Loaded ${foundDevices.size} bonded devices")
        } catch (e: Exception) {
            Log.e(TAG, "Error loading bonded devices", e)
        }
    }

    // --------------------------------------------------
    // SCAN
    // --------------------------------------------------

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun startScan(adapter: BluetoothAdapter) {
        if (scanner == null) {
            try {
                scanner = adapter.bluetoothLeScanner
            } catch (e: SecurityException) {
                Log.e(TAG, "Failed to initialize scanner", e)
                return
            }
        }
        if (foundDevices.isEmpty()) loadBondedDevices()
        Log.d(TAG, "Starting BLE scan")
        scanner?.startScan(scanCallback)
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun stopScan() {
        scanner?.stopScan(scanCallback)
    }

    private val scanCallback = object : ScanCallback() {
        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val device = result.device ?: return
            val name = device.name ?: return
            val address = device.address ?: return
            if (!foundDevices.containsKey(address) || foundDevices[address]!!.isPairedOnly) {
                foundDevices[address] = Device(name, address, isPairedOnly = false)
                _devicesFlow.value = foundDevices.values.toList()
                Log.d(TAG, "Device found: $name - $address")
            }
        }
    }

    // --------------------------------------------------
    // CONNECT
    // --------------------------------------------------

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connect(device: Device) {
        Log.d(TAG, "Connecting to ${device.address}")
        _connectionReady.value = false
        gatt = adapter.getRemoteDevice(device.address)
            .connectGatt(context, false, gattCallback)
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun disconnect() {
        gatt?.disconnect()
        gatt?.close()
        gatt = null
    }

    // --------------------------------------------------
    // SESSION REQUEST
    // --------------------------------------------------

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun requestSessions() {
        val service = gatt?.getService(SERVICE_UUID) ?: run {
            Log.e(TAG, "requestSessions: GATT not connected")
            return
        }
        val requestChar = service.getCharacteristic(SESSION_REQUEST_CHAR_UUID) ?: run {
            Log.e(TAG, "Session request characteristic not found")
            return
        }
        requestChar.value = "GET_SESSIONS".toByteArray(Charsets.UTF_8)
        gatt?.writeCharacteristic(requestChar)
        Log.d(TAG, "GET_SESSIONS command sent")
    }

    // --------------------------------------------------
    // GATT CALLBACK
    // --------------------------------------------------

    private val gattCallback = object : BluetoothGattCallback() {

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.d(TAG, "Connected → discovering services")
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.d(TAG, "Disconnected")
                _connectionReady.value = false
            }
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            Log.d(TAG, "Services discovered")
            val service = gatt.getService(SERVICE_UUID) ?: return

            // Subscribe to sensor data characteristic first; session response CCCD
            // is written in onDescriptorWrite after this one completes.
            val sensorChar = service.getCharacteristic(CHAR_UUID)
            if (sensorChar != null) {
                gatt.setCharacteristicNotification(sensorChar, true)
                sensorChar.getDescriptor(CCCD_UUID)?.let { desc ->
                    desc.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                    gatt.writeDescriptor(desc)
                }
            }

            pendingSessionCharSubscription = service.getCharacteristic(SESSION_RESPONSE_CHAR_UUID)
            pendingSessionCharSubscription?.let { gatt.setCharacteristicNotification(it, true) }
        }

        @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
        override fun onDescriptorWrite(
            gatt: BluetoothGatt,
            descriptor: BluetoothGattDescriptor,
            status: Int
        ) {
            val sessionChar = pendingSessionCharSubscription
            if (sessionChar != null) {
                pendingSessionCharSubscription = null
                sessionChar.getDescriptor(CCCD_UUID)?.let { desc ->
                    desc.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                    gatt.writeDescriptor(desc)
                    Log.d(TAG, "Session response characteristic subscribed")
                }
            } else {
                // Both CCCDs written — Pi is subscribed, safe to request sessions
                _connectionReady.value = true
                Log.d(TAG, "BLE connection fully ready")
            }
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            val value = characteristic.value?.toString(Charsets.UTF_8) ?: ""
            when (characteristic.uuid) {
                CHAR_UUID -> {
                    Log.d(TAG, "Sensor data: $value")
                    _dataFlow.value = value
                }
                SESSION_RESPONSE_CHAR_UUID -> {
                    Log.d(TAG, "Session data: $value")
                    _sessionFlow.value = value
                }
            }
        }
    }
}
