package com.example.vehiculardataanalysis.screens.viewmodel

import android.Manifest
import android.bluetooth.BluetoothAdapter
import androidx.annotation.RequiresPermission
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.screens.data.BleRepository
import com.example.vehiculardataanalysis.domain.Device
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class DeviceViewModel(
    private val repo: BleRepository
) : ViewModel() {

    private val _devices = MutableStateFlow<List<Device>>(emptyList())
    val devices: StateFlow<List<Device>> = _devices

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun startScan(adapter: BluetoothAdapter) {
        repo.startScan(adapter)

        viewModelScope.launch {
            repo.scannedDevices.collect {
                _devices.value = it
            }
        }
    }


}