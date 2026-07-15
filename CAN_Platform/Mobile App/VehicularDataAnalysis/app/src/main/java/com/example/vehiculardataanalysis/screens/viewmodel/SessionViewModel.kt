package com.example.vehiculardataanalysis.screens.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.vehiculardataanalysis.domain.SessionInfo
import com.example.vehiculardataanalysis.screens.data.BleRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// ── Base async state — shared Idle / Loading / Error variants ─────────────────

sealed interface AsyncState {
    object Idle    : AsyncState, SessionListState, SessionStatsState, SessionActionState
    object Loading : AsyncState, SessionListState, SessionStatsState, SessionActionState
    data class Error(val message: String) : AsyncState, SessionListState, SessionStatsState, SessionActionState
}

// ── Concrete state types — each adds only its own Loaded payload ──────────────

sealed interface SessionListState : AsyncState {
    data class Loaded(val sessions: List<SessionInfo>) : SessionListState
}

sealed interface SessionStatsState : AsyncState {
    data class Loaded(val sessionId: Int, val stats: OverallVehicleStats) : SessionStatsState
}

sealed interface SessionActionState : AsyncState

data class OverallVehicleStats(
    val avgRpm: Int,
    val maxRpm: Int,
    val avgClt: Float,
    val maxVss: Float,
)

// ── Single unified UI state ────────────────────────────────────────────────────

data class SessionUiState(
    val sessionList:  SessionListState  = AsyncState.Idle,
    val vehicleStats: OverallVehicleStats? = null,
    val sessionStats: SessionStatsState = AsyncState.Idle,
    val actionState:  SessionActionState = AsyncState.Idle,
)

// ── ViewModel ─────────────────────────────────────────────────────────────────

private enum class PendingRequest { NONE, SESSION_LIST, SESSION_STATS, SESSION_ACTION }

class SessionViewModel(
    private val repository: BleRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(SessionUiState())
    val uiState: StateFlow<SessionUiState> = _uiState.asStateFlow()

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
                    line.isBlank()                      -> {}
                    line == "END"                       -> {
                        if (pendingRequest == PendingRequest.SESSION_LIST) {
                            _uiState.update { it.copy(sessionList = SessionListState.Loaded(buffer.toList())) }
                            buffer.clear()
                        }
                        pendingRequest = PendingRequest.NONE
                    }
                    line.startsWith("ERR:")             -> {
                        val msg = line.removePrefix("ERR:")
                        when (pendingRequest) {
                            PendingRequest.SESSION_LIST   -> {
                                _uiState.update { it.copy(sessionList = AsyncState.Error(msg)) }
                                buffer.clear()
                            }
                            PendingRequest.SESSION_STATS  ->
                                _uiState.update { it.copy(sessionStats = AsyncState.Error(msg)) }
                            PendingRequest.SESSION_ACTION ->
                                _uiState.update { it.copy(actionState = AsyncState.Error(msg)) }
                            PendingRequest.NONE           -> {}
                        }
                        pendingRequest = PendingRequest.NONE
                    }
                    line.startsWith("OVERALL:")         -> parseOverallStats(line.removePrefix("OVERALL:"))
                    line.startsWith("SESSION_STATS:")   -> parseSessionStats(line.removePrefix("SESSION_STATS:"))
                    line.startsWith("SESSION_CREATED:") -> {
                        _uiState.update { it.copy(actionState = AsyncState.Idle) }
                        pendingRequest = PendingRequest.NONE
                        requestSessions()
                    }
                    line.startsWith("SESSION_ENDED:")   -> {
                        _uiState.update { it.copy(actionState = AsyncState.Idle) }
                        pendingRequest = PendingRequest.NONE
                        requestSessions()
                    }
                    else                                -> parseSessionLine(line)?.let { buffer.add(it) }
                }
            }
        }
    }

    // ── Public commands ────────────────────────────────────────────────────────

    fun requestSessions() {
        buffer.clear()
        _uiState.update { it.copy(sessionList = AsyncState.Loading, vehicleStats = null) }
        pendingRequest = PendingRequest.SESSION_LIST
        repository.requestSessions()
    }

    fun requestSessionStats(sessionId: Int) {
        _uiState.update { it.copy(sessionStats = AsyncState.Loading) }
        pendingRequest = PendingRequest.SESSION_STATS
        repository.requestSessionStats(sessionId)
    }

    fun createSession() {
        _uiState.update { it.copy(actionState = AsyncState.Loading) }
        pendingRequest = PendingRequest.SESSION_ACTION
        repository.createSession()
    }

    fun endSession() {
        _uiState.update { it.copy(actionState = AsyncState.Loading) }
        pendingRequest = PendingRequest.SESSION_ACTION
        repository.endSession()
    }

    fun clearActionError() {
        _uiState.update { it.copy(actionState = AsyncState.Idle) }
    }

    // ── Mock / test-device helpers ─────────────────────────────────────────────

    fun startMockSessions() {
        val now = System.currentTimeMillis() / 1000.0
        _uiState.update {
            it.copy(
                vehicleStats = OverallVehicleStats(avgRpm = 2350, maxRpm = 5200, avgClt = 87.5f, maxVss = 142.3f),
                sessionList  = SessionListState.Loaded(
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
            )
        }
    }

    fun startMockCreateSession() {
        val now      = System.currentTimeMillis() / 1000.0
        val current  = (_uiState.value.sessionList as? SessionListState.Loaded)?.sessions ?: emptyList()
        val updated  = current.map { s ->
            if (s.durationSeconds < 0) s.copy(durationSeconds = now - s.startEpoch) else s
        } + SessionInfo(
            id              = (current.maxOfOrNull { it.id } ?: 0) + 1,
            startEpoch      = now,
            durationSeconds = -1.0
        )
        _uiState.update { it.copy(sessionList = SessionListState.Loaded(updated), actionState = AsyncState.Idle) }
    }

    fun startMockEndSession() {
        val now     = System.currentTimeMillis() / 1000.0
        val current = (_uiState.value.sessionList as? SessionListState.Loaded)?.sessions ?: emptyList()
        val updated = current.map { s ->
            if (s.durationSeconds < 0) s.copy(durationSeconds = now - s.startEpoch) else s
        }
        _uiState.update { it.copy(sessionList = SessionListState.Loaded(updated), actionState = AsyncState.Idle) }
    }

    fun startMockSessionStats(sessionId: Int) {
        _uiState.update {
            it.copy(
                sessionStats = SessionStatsState.Loaded(
                    sessionId = sessionId,
                    stats     = OverallVehicleStats(
                        avgRpm = 2100 + sessionId * 50,
                        maxRpm = 4800 + sessionId * 100,
                        avgClt = 85f  + sessionId * 0.5f,
                        maxVss = 110f + sessionId * 3f,
                    )
                )
            )
        }
    }

    // ── Parsers ────────────────────────────────────────────────────────────────

    private fun parseSessionStats(data: String) {
        try {
            val p = data.split(",")
            _uiState.update {
                it.copy(
                    sessionStats = SessionStatsState.Loaded(
                        sessionId = p[0].toInt(),
                        stats     = OverallVehicleStats(
                            avgRpm = p[1].toFloat().toInt(),
                            maxRpm = p[2].toIntOrNull() ?: 0,
                            avgClt = p[3].toFloatOrNull() ?: 0f,
                            maxVss = p[4].toFloatOrNull() ?: 0f,
                        )
                    )
                )
            }
        } catch (_: Exception) {}
    }

    private fun parseSessionLine(line: String): SessionInfo? = try {
        val parts = line.split(",")
        SessionInfo(
            id              = parts[0].toInt(),
            startEpoch      = parts[1].toDouble(),
            durationSeconds = parts[2].toDouble()
        )
    } catch (_: Exception) { null }

    private fun parseOverallStats(data: String) {
        try {
            val p = data.split(",")
            _uiState.update {
                it.copy(
                    vehicleStats = OverallVehicleStats(
                        avgRpm = p[0].toFloat().toInt(),
                        maxRpm = p[1].toIntOrNull() ?: 0,
                        avgClt = p[2].toFloatOrNull() ?: 0f,
                        maxVss = p[3].toFloatOrNull() ?: 0f,
                    )
                )
            }
        } catch (_: Exception) {}
    }
}
