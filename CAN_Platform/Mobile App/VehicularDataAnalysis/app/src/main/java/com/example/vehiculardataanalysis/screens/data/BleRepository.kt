package com.example.vehiculardataanalysis.screens.data

import android.Manifest
import android.bluetooth.BluetoothAdapter
import androidx.annotation.RequiresPermission
import com.example.bleapp.data.BleManager
import com.example.vehiculardataanalysis.domain.Device
import kotlinx.coroutines.flow.Flow

class BleRepository(
    private val manager: BleManager
) {

    val scannedDevices: Flow<List<Device>> = manager.devicesFlow

    // CanData Future Change
    val canData: Flow<String> = manager.dataFlow

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun startScan(adapter: BluetoothAdapter) {
        manager.startScan(adapter)
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connectToDevice(device: Device) {
        manager.connect(device)
    }
}