package com.example.vehiculardataanalysis.screens.display

import android.bluetooth.BluetoothAdapter
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.screens.data.BleRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class DataUiState(
    val rpm: Int = 0,
    val temp: Float = 0f,
    val afr: Float = 0f,
    val raw: String = "Waiting...",
    val isConnected: Boolean = false
)

class DataDisplayViewModel(
    private val repository: BleRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(DataUiState())
    val uiState: StateFlow<DataUiState> = _uiState.asStateFlow()

    fun start(adapter: BluetoothAdapter) {
        repository.start(adapter)

        viewModelScope.launch {
            repository.canData.collect { data ->
                _uiState.update {
                    it.copy(
                        rpm = data.rpm ?: 0,
                        temp = data.temp ?: 0f,
                        afr = data.afr ?: 0f,
                        raw = data.raw,
                        isConnected = true
                    )
                }
            }
        }
    }
}