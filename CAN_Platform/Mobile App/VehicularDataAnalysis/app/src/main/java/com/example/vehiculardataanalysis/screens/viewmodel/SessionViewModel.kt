package com.example.vehiculardataanalysis.screens.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.domain.SessionInfo
import com.example.vehiculardataanalysis.screens.data.BleRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed class SessionListState {
    object Idle : SessionListState()
    object Loading : SessionListState()
    data class Loaded(val sessions: List<SessionInfo>) : SessionListState()
    data class Error(val message: String) : SessionListState()
}

sealed class SessionStatsState {
    object Idle : SessionStatsState()
    object Loading : SessionStatsState()
    data class Loaded(val sessionId: Int, val stats: OverallVehicleStats) : SessionStatsState()
    data class Error(val message: String) : SessionStatsState()
}

data class OverallVehicleStats(
    val avgRpm: Int,
    val maxRpm: Int,
    val avgClt: Float,
    val maxVss: Float,
)

private enum class PendingRequest { NONE, SESSION_LIST, SESSION_STATS }

class SessionViewModel(
    private val repository: BleRepository
) : ViewModel() {

    private val _state = MutableStateFlow<SessionListState>(SessionListState.Idle)
    val state: StateFlow<SessionListState> = _state.asStateFlow()

    private val _vehicleStats = MutableStateFlow<OverallVehicleStats?>(null)
    val vehicleStats: StateFlow<OverallVehicleStats?> = _vehicleStats.asStateFlow()

    private val _sessionStatsState = MutableStateFlow<SessionStatsState>(SessionStatsState.Idle)
    val sessionStatsState: StateFlow<SessionStatsState> = _sessionStatsState.asStateFlow()

    private val buffer = mutableListOf<SessionInfo>()
    private var pendingRequest = PendingRequest.NONE

    init {
        viewModelScope.launch(Dispatchers.Default) {
            repository.connectionReady.collect { ready ->
                if (ready) requestSessions()
            }
        }

        viewModelScope.launch(Dispatchers.Default) {
            repository.sessionData.collect { line ->
                when {
                    line.isBlank()                     -> {}
                    line == "END"                      -> {
                        if (pendingRequest == PendingRequest.SESSION_LIST) {
                            _state.value = SessionListState.Loaded(buffer.toList())
                            buffer.clear()
                        }
                        pendingRequest = PendingRequest.NONE
                    }
                    line.startsWith("ERR:")            -> {
                        if (pendingRequest == PendingRequest.SESSION_LIST) {
                            _state.value = SessionListState.Error(line.removePrefix("ERR:"))
                            buffer.clear()
                        } else if (pendingRequest == PendingRequest.SESSION_STATS) {
                            _sessionStatsState.value = SessionStatsState.Error(line.removePrefix("ERR:"))
                        }
                        pendingRequest = PendingRequest.NONE
                    }
                    line.startsWith("OVERALL:")        -> parseOverallStats(line.removePrefix("OVERALL:"))
                    line.startsWith("SESSION_STATS:")  -> parseSessionStats(line.removePrefix("SESSION_STATS:"))
                    else                               -> parseSessionLine(line)?.let { buffer.add(it) }
                }
            }
        }
    }

    fun requestSessions() {
        buffer.clear()
        _vehicleStats.value = null
        _state.value = SessionListState.Loading
        pendingRequest = PendingRequest.SESSION_LIST
        repository.requestSessions()
    }

    fun requestSessionStats(sessionId: Int) {
        _sessionStatsState.value = SessionStatsState.Loading
        pendingRequest = PendingRequest.SESSION_STATS
        repository.requestSessionStats(sessionId)
    }

    fun startMockSessions() {
        val now = System.currentTimeMillis() / 1000.0
        _vehicleStats.value = OverallVehicleStats(
            avgRpm = 2350,
            maxRpm = 5200,
            avgClt = 87.5f,
            maxVss = 142.3f,
        )
        _state.value = SessionListState.Loaded(
            listOf(
                SessionInfo(id = 1, startEpoch = now - 30 * 86400, durationSeconds = 1823.0),
                SessionInfo(id = 2, startEpoch = now - 22 * 86400, durationSeconds = 3601.0),
                SessionInfo(id = 3, startEpoch = now - 18 * 86400, durationSeconds =  542.0),
                SessionInfo(id = 4, startEpoch = now - 14 * 86400, durationSeconds = 7265.0),
                SessionInfo(id = 5, startEpoch = now - 10 * 86400, durationSeconds =  285.0),
                SessionInfo(id = 6, startEpoch = now -  7 * 86400, durationSeconds = 4512.0),
                SessionInfo(id = 7, startEpoch = now -  3 * 86400, durationSeconds = 2178.0),
                SessionInfo(id = 8, startEpoch = now -      86400, durationSeconds =  934.0),
                SessionInfo(id = 9, startEpoch = now -       3600, durationSeconds =   -1.0),
            )
        )
    }

    fun startMockSessionStats(sessionId: Int) {
        _sessionStatsState.value = SessionStatsState.Loaded(
            sessionId = sessionId,
            stats = OverallVehicleStats(
                avgRpm = 2100 + sessionId * 50,
                maxRpm = 4800 + sessionId * 100,
                avgClt = 85f + sessionId * 0.5f,
                maxVss = 110f + sessionId * 3f,
            )
        )
    }

    private fun parseSessionStats(data: String) {
        try {
            val p = data.split(",")
            val sessionId = p[0].toInt()
            _sessionStatsState.value = SessionStatsState.Loaded(
                sessionId = sessionId,
                stats = OverallVehicleStats(
                    avgRpm = p[1].toFloat().toInt(),
                    maxRpm = p[2].toIntOrNull() ?: 0,
                    avgClt = p[3].toFloatOrNull() ?: 0f,
                    maxVss = p[4].toFloatOrNull() ?: 0f,
                )
            )
        } catch (_: Exception) {}
    }

    private fun parseSessionLine(line: String): SessionInfo? = try {
        val parts = line.split(",")
        SessionInfo(
            id              = parts[0].toInt(),
            startEpoch      = parts[1].toDouble(),
            durationSeconds = parts[2].toDouble()
        )
    } catch (e: Exception) {
        null
    }

    private fun parseOverallStats(data: String) {
        try {
            val p = data.split(",")
            _vehicleStats.value = OverallVehicleStats(
                avgRpm = p[0].toFloat().toInt(),
                maxRpm = p[1].toIntOrNull() ?: 0,
                avgClt = p[2].toFloatOrNull() ?: 0f,
                maxVss = p[3].toFloatOrNull() ?: 0f,
            )
        } catch (_: Exception) {}
    }
}
