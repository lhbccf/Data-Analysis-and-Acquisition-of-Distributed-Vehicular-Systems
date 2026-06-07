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

class SessionViewModel(
    private val repository: BleRepository
) : ViewModel() {

    private val _state = MutableStateFlow<SessionListState>(SessionListState.Idle)
    val state: StateFlow<SessionListState> = _state.asStateFlow()

    private val buffer = mutableListOf<SessionInfo>()

    init {
        viewModelScope.launch(Dispatchers.Default) {
            repository.sessionData.collect { line ->
                when {
                    line.isBlank() -> {}
                    line == "END" -> {
                        _state.value = SessionListState.Loaded(buffer.toList())
                        buffer.clear()
                    }
                    line.startsWith("ERR:") -> {
                        _state.value = SessionListState.Error(line.removePrefix("ERR:"))
                        buffer.clear()
                    }
                    else -> parseSessionLine(line)?.let { buffer.add(it) }
                }
            }
        }
    }

    fun requestSessions() {
        buffer.clear()
        _state.value = SessionListState.Loading
        repository.requestSessions()
    }

    fun startMockSessions() {
        val now = System.currentTimeMillis() / 1000.0
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
}
