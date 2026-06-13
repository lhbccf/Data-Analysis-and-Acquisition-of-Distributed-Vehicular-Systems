package com.example.vehiculardataanalysis.screens.viewmodel


import android.Manifest
import android.bluetooth.BluetoothAdapter
import androidx.annotation.RequiresPermission
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.data.BleRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlin.random.Random

data class MainUiState(
    val rpm: Int = 0,
    val temp: Float = 0f,
    val afr: Float = 0f,
    val tps: Float = 0f,
    val map: Float = 0f,
    val battery: Float = 0f,
    val dwell: Float = 0f,
    val timing: Float = 0f,
    val vss: Float = 0f,
    val iat: Float = 0f,
    val ego_cor: Float = 0f,
    val ve: Float = 0f,
    val sync: Int = 0,
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
            repository.canData
                .flowOn(Dispatchers.Default)
                .collect { rawData ->
                    if (rawData.isBlank()) return@collect
                    val newState = parseCanData(rawData)
                    viewModelScope.launch(Dispatchers.Main) {
                        _uiState.value = newState
                    }
                }
        }
    }

    @RequiresPermission(Manifest.permission.BLUETOOTH_CONNECT)
    fun connect(device: Device) {
        repository.connectToDevice(device)
    }

    fun startMockData() {
        var currentRpm     = 2000
        var currentTemp    = 80f
        var currentAfr     = 14.2f
        var currentTps     = 15f
        var currentMap     = 50f
        var currentBattery = 12.5f
        var currentDwell   = 5f
        var currentTiming  = 10f
        var currentVss     = 30f
        var currentIat     = 35f
        var currentEgoCor  = 100f
        var currentVe      = 55f
        var currentSync    = 1

        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                delay(100)

                currentRpm     = (currentRpm + Random.nextInt(-150, 150)).coerceIn(700, 8000)
                currentTemp    = (currentTemp + Random.nextFloat() * 0.4f - 0.2f).coerceIn(20f, 120f)
                currentAfr     = (currentAfr + Random.nextFloat() * 0.1f - 0.05f).coerceIn(10f, 20f)
                currentTps     = (currentTps + Random.nextFloat() * 3f - 1.5f).coerceIn(0f, 100f)
                currentMap     = (currentMap + Random.nextFloat() * 5f - 2.5f).coerceIn(30f, 200f)
                currentBattery = (currentBattery + Random.nextFloat() * 0.04f - 0.02f).coerceIn(8f, 18f)
                currentDwell   = (currentDwell + Random.nextFloat() * 0.2f - 0.1f).coerceIn(2f, 6f)
                currentTiming  = (currentTiming + Random.nextFloat() * 1f - 0.5f).coerceIn(5f, 30f)
                currentVss     = (currentVss + Random.nextFloat() * 4f - 2f).coerceIn(0f, 250f)
                currentIat     = (currentIat + Random.nextFloat() * 0.2f - 0.1f).coerceIn(-40f, 120f)
                currentEgoCor  = (currentEgoCor + Random.nextFloat() * 1f - 0.5f).coerceIn(70f, 130f)
                currentVe      = (currentVe + Random.nextFloat() * 2f - 1f).coerceIn(0f, 120f)

                launch(Dispatchers.Main) {
                    _uiState.update {
                        it.copy(
                            rpm     = currentRpm,
                            temp    = currentTemp,
                            afr     = currentAfr,
                            tps     = currentTps,
                            map     = currentMap,
                            battery = currentBattery,
                            dwell   = currentDwell,
                            timing  = currentTiming,
                            vss     = currentVss,
                            iat     = currentIat,
                            ego_cor = currentEgoCor,
                            ve      = currentVe,
                            sync    = currentSync,
                            raw     = "$currentRpm,$currentTemp,$currentAfr,$currentTps,$currentMap," +
                                      "$currentBattery,$currentDwell,$currentTiming,$currentVss," +
                                      "$currentIat,$currentEgoCor,$currentVe,$currentSync"
                        )
                    }
                }
            }
        }
    }

    private fun parseCanData(rawData: String): MainUiState {
        return try {
            val p = rawData.split(",").map { it.trim() }
            MainUiState(
                rpm     = p.getOrNull(0)?.toIntOrNull()   ?: 0,
                temp    = p.getOrNull(1)?.toFloatOrNull() ?: 0f,
                afr     = p.getOrNull(2)?.toFloatOrNull() ?: 0f,
                tps     = p.getOrNull(3)?.toFloatOrNull() ?: 0f,
                map     = p.getOrNull(4)?.toFloatOrNull() ?: 0f,
                battery = p.getOrNull(5)?.toFloatOrNull() ?: 0f,
                dwell   = p.getOrNull(6)?.toFloatOrNull() ?: 0f,
                timing  = p.getOrNull(7)?.toFloatOrNull() ?: 0f,
                vss     = p.getOrNull(8)?.toFloatOrNull() ?: 0f,
                iat     = p.getOrNull(9)?.toFloatOrNull() ?: 0f,
                ego_cor = p.getOrNull(10)?.toFloatOrNull() ?: 0f,
                ve      = p.getOrNull(11)?.toFloatOrNull() ?: 0f,
                sync    = p.getOrNull(12)?.toIntOrNull()   ?: 0,
                raw     = rawData
            )
        } catch (e: Exception) {
            MainUiState(raw = rawData)
        }
    }
}