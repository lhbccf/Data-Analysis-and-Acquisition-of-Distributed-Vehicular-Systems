package com.example.vehiculardataanalysis.screens.data

import android.Manifest
import android.bluetooth.*
import android.bluetooth.le.*
import android.content.Context
import androidx.annotation.RequiresPermission
import kotlinx.coroutines.flow.MutableStateFlow
import java.util.*

class BleManager(private val context: Context) {

    private val _dataFlow = MutableStateFlow("")
    val dataFlow = _dataFlow

    private val SERVICE_UUID =
        UUID.fromString("12345678-1234-5678-1234-56789abcdef0")

    private val CHAR_UUID =
        UUID.fromString("abcdef01-1234-5678-1234-56789abcdef0")

    private var gatt: BluetoothGatt? = null

    fun startScan(adapter: BluetoothAdapter) {
        val scanner = adapter.bluetoothLeScanner

        scanner.startScan(object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult) {
                if (result.device.name == "MyPiBLE") {
                    scanner.stopScan(this)
                    connect(result.device)
                }
            }
        })
    }

    private fun connect(device: BluetoothDevice) {
        gatt = device.connectGatt(context, false, gattCallback)
    }

    private val gattCallback = object : BluetoothGattCallback() {

        override fun onConnectionStateChange(
            gatt: BluetoothGatt,
            status: Int,
            newState: Int
        ) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                gatt.discoverServices()
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            val service = gatt.getService(SERVICE_UUID)
            val characteristic = service.getCharacteristic(CHAR_UUID)

            gatt.setCharacteristicNotification(characteristic, true)

            val descriptor = characteristic.getDescriptor(
                UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
            )

            descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
            gatt.writeDescriptor(descriptor)
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            val value = characteristic.value.toString(Charsets.UTF_8)
            _dataFlow.value = value
        }
    }
}