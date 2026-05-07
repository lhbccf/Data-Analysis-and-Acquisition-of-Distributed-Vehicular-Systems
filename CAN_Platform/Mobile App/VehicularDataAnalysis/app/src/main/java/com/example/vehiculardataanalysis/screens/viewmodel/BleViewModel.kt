package com.example.vehiculardataanalysis.screens.viewmodel


import android.Manifest
import android.bluetooth.BluetoothAdapter
import androidx.annotation.RequiresPermission
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.data.BleRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class MainUiState(
    val data: String = ""
    /**
    val rpm: Int = 0,
    val temp: Float = 0f,
    val afr: Float = 0f,
    val raw: String = "Waiting...",
    val isConnected: Boolean = false
    **/
)

class BleViewModel(
    private val repository: BleRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    @RequiresPermission(Manifest.permission.BLUETOOTH_SCAN)
    fun start(adapter: BluetoothAdapter) {
        repository.startScan(adapter)

        viewModelScope.launch {
            repository.canData.collect { data ->
                _uiState.update {
                    /**
                    it.copy(
                        rpm = data.rpm ?: 0,
                        temp = data.temp ?: 0f,
                        afr = data.afr ?: 0f,
                        raw = data.raw,
                        isConnected = true
                    )
                    **/
                    it.copy(data = data)
                }
            }
        }
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connect(device: Device) {
        repository.connectToDevice(device)
    }
}