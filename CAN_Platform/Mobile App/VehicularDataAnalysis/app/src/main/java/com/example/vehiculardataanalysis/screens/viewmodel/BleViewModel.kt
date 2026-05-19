package com.example.vehiculardataanalysis.screens.viewmodel


import android.Manifest
import android.bluetooth.BluetoothAdapter
import androidx.annotation.RequiresPermission
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.domain.CanData
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.data.BleRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class MainUiState(
    val rpm: Int = 0,
    val temp: Float = 0f,
    val afr: Float = 0f,
    val tps: Float = 0f,
    val map: Float = 0f,
    val battery: Float = 0f,
    val dwell: Float = 0f,
    val timing: Float = 0f,
    val raw: String = "Waiting for data..."
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
            repository.canData.collect { rawData ->
                val parsed = parseCanData(rawData)
                _uiState.update {
                    it.copy(
                        rpm = parsed.rpm ?: 0,
                        temp = parsed.temp ?: 0f,
                        afr = parsed.afr ?: 0f,
                        raw = rawData
                    )
                }
            }
        }
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connect(device: Device) {
        repository.connectToDevice(device)
    }

    private fun parseCanData(rawData: String): CanData {
        return try {
            val parts = rawData.split(",").map { it.trim() }
            CanData(
                rpm = parts.getOrNull(0)?.toIntOrNull(),
                temp = parts.getOrNull(1)?.toFloatOrNull(),
                afr = parts.getOrNull(2)?.toFloatOrNull(),
                raw = rawData
            )
        } catch (e: Exception) {
            CanData(raw = rawData)
        }
    }
}