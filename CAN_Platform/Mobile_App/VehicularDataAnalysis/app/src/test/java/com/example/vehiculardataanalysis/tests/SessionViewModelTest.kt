package com.example.vehiculardataanalysis.tests

import com.example.vehiculardataanalysis.screens.data.BleRepository
import com.example.vehiculardataanalysis.screens.viewmodel.AsyncState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionListState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionStatsState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionViewModel
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/**
 * SessionViewModel owns the line-based BLE session protocol (device -> phone) and the
 * create/end-session state machine. Malformed input from the device must never crash the
 * UI layer, so most tests here exercise recovery from bad data as much as the happy path.
 */
class SessionViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: BleRepository
    private lateinit var connectionReady: MutableSharedFlow<Boolean>
    private lateinit var sessionData: MutableSharedFlow<String>
    private lateinit var viewModel: SessionViewModel

    private val timeoutMs = 2_000L

    @Before
    fun setUp() {
        connectionReady = MutableSharedFlow(extraBufferCapacity = 16)
        sessionData = MutableSharedFlow(extraBufferCapacity = 64)
        repository = mockk(relaxed = true)
        every { repository.connectionReady } returns connectionReady
        every { repository.sessionData } returns sessionData

        viewModel = SessionViewModel(repository)
    }

    private suspend fun emitLines(vararg lines: String) {
        sessionData.subscriptionCount.first { it > 0 }
        lines.forEach { sessionData.emit(it) }
    }

    // ── requestSessions / connection lifecycle ─────────────────────────────

    @Test
    fun `requestSessions moves state to Loading and calls repository`() {
        viewModel.requestSessions()

        assertTrue(viewModel.uiState.value.sessionList is AsyncState.Loading)
        verify { repository.requestSessions() }
    }

    @Test
    fun `connection becoming ready automatically requests sessions`() = runBlocking {
        connectionReady.subscriptionCount.first { it > 0 }
        connectionReady.emit(true)

        withTimeout(timeoutMs) { viewModel.uiState.first { it.sessionList is AsyncState.Loading } }
        verify { repository.requestSessions() }
    }

    // ── Session list parsing ────────────────────────────────────────────────

    @Test
    fun `valid session lines are buffered and committed on END`() = runBlocking {
        viewModel.requestSessions()
        emitLines("1,1690000000.0,120.5", "2,1690000500.0,30.0", "END")

        val state = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.sessionList is SessionListState.Loaded }
        }.sessionList as SessionListState.Loaded

        assertEquals(2, state.sessions.size)
        assertEquals(1, state.sessions[0].id)
        assertEquals(1690000000.0, state.sessions[0].startEpoch, 0.0001)
        assertEquals(120.5, state.sessions[0].durationSeconds, 0.0001)
    }

    @Test
    fun `malformed session line is skipped without dropping valid ones`() = runBlocking {
        viewModel.requestSessions()
        emitLines("not,a,valid,line", "3,1690000000.0,60.0", "garbage", "END")

        val state = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.sessionList is SessionListState.Loaded }
        }.sessionList as SessionListState.Loaded

        assertEquals(1, state.sessions.size)
        assertEquals(3, state.sessions[0].id)
    }

    @Test
    fun `blank lines are ignored and do not terminate buffering`() = runBlocking {
        viewModel.requestSessions()
        emitLines("1,100.0,5.0", "", "   ", "2,200.0,10.0", "END")

        val state = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.sessionList is SessionListState.Loaded }
        }.sessionList as SessionListState.Loaded

        assertEquals(2, state.sessions.size)
    }

    @Test
    fun `ERR while listing sessions produces Error state and clears the buffer`() = runBlocking {
        viewModel.requestSessions()
        emitLines("1,100.0,5.0", "ERR:device disconnected")

        val sessionList = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.sessionList is AsyncState.Error }
        }.sessionList as AsyncState.Error

        assertEquals("device disconnected", sessionList.message)
    }

    // ── Overall vehicle stats ("OVERALL:") ──────────────────────────────────

    @Test
    fun `OVERALL line parses vehicle stats`() = runBlocking {
        emitLines("OVERALL:2500.4,6000,90.5,180.2")

        val stats = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.vehicleStats != null }
        }.vehicleStats!!

        assertEquals(2500, stats.avgRpm)
        assertEquals(6000, stats.maxRpm)
        assertEquals(90.5f, stats.avgClt, 0.0001f)
        assertEquals(180.2f, stats.maxVss, 0.0001f)
    }

    @Test
    fun `OVERALL line with non-numeric optional fields falls back to zero`() = runBlocking {
        emitLines("OVERALL:1800.0,notanumber,notanumber,notanumber")

        val stats = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.vehicleStats != null }
        }.vehicleStats!!

        assertEquals(1800, stats.avgRpm)
        assertEquals(0, stats.maxRpm)
        assertEquals(0f, stats.avgClt, 0.0001f)
        assertEquals(0f, stats.maxVss, 0.0001f)
    }

    @Test
    fun `malformed OVERALL line does not crash the collector`() = runBlocking {
        // A missing/non-numeric required field throws inside the parser; it must be
        // swallowed so the next valid line still updates state instead of the
        // collector coroutine dying silently.
        emitLines("OVERALL:notanumber,6000,90.5,180.2")
        emitLines("OVERALL:2500.0,6000,90.5,180.2")

        val stats = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.vehicleStats?.avgRpm == 2500 }
        }.vehicleStats!!

        assertEquals(6000, stats.maxRpm)
    }

    // ── Per-session stats ("SESSION_STATS:") ────────────────────────────────

    @Test
    fun `SESSION_STATS line parses into sessionStats state`() = runBlocking {
        viewModel.requestSessionStats(3)
        emitLines("SESSION_STATS:3,2100.0,4800,85.0,120.0")

        val stats = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.sessionStats is SessionStatsState.Loaded }
        }.sessionStats as SessionStatsState.Loaded

        assertEquals(3, stats.sessionId)
        assertEquals(2100, stats.stats.avgRpm)
        assertEquals(4800, stats.stats.maxRpm)
    }

    @Test
    fun `ERR while requesting session stats only affects sessionStats state`() = runBlocking {
        viewModel.requestSessions()
        emitLines("1,100.0,5.0", "END")
        withTimeout(timeoutMs) { viewModel.uiState.first { it.sessionList is SessionListState.Loaded } }

        viewModel.requestSessionStats(9)
        emitLines("ERR:no such session")

        val state = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.sessionStats is AsyncState.Error }
        }
        assertEquals("no such session", (state.sessionStats as AsyncState.Error).message)
        // Unrelated state must be untouched by an error scoped to session stats.
        assertTrue(state.sessionList is SessionListState.Loaded)
    }

    // ── Create / end session action state machine ───────────────────────────

    @Test
    fun `createSession then SESSION_CREATED clears loading and re-requests sessions`() = runBlocking {
        viewModel.createSession()
        assertTrue(viewModel.uiState.value.actionState is AsyncState.Loading)

        emitLines("SESSION_CREATED:7")

        withTimeout(timeoutMs) { viewModel.uiState.first { it.actionState is AsyncState.Idle } }
        verify(exactly = 1) { repository.createSession() }
        verify(exactly = 1) { repository.requestSessions() }
    }

    @Test
    fun `endSession then SESSION_ENDED clears loading and re-requests sessions`() = runBlocking {
        viewModel.endSession()
        assertTrue(viewModel.uiState.value.actionState is AsyncState.Loading)

        emitLines("SESSION_ENDED:7")

        withTimeout(timeoutMs) { viewModel.uiState.first { it.actionState is AsyncState.Idle } }
        verify(exactly = 1) { repository.endSession() }
        verify(exactly = 1) { repository.requestSessions() }
    }

    @Test
    fun `ERR while creating a session surfaces an action error`() = runBlocking {
        viewModel.createSession()
        emitLines("ERR:battery too low to start session")

        val actionState = withTimeout(timeoutMs) {
            viewModel.uiState.first { it.actionState is AsyncState.Error }
        }.actionState as AsyncState.Error

        assertEquals("battery too low to start session", actionState.message)
    }

    @Test
    fun `clearActionError resets action state to Idle`() {
        viewModel.createSession()
        assertTrue(viewModel.uiState.value.actionState is AsyncState.Loading)

        viewModel.clearActionError()

        assertTrue(viewModel.uiState.value.actionState is AsyncState.Idle)
    }

    // ── Mock/test-device helpers (used by the "Test Device" flow in the UI) ─

    @Test
    fun `startMockSessions seeds a deterministic session list with one ongoing session`() {
        viewModel.startMockSessions()

        val state = viewModel.uiState.value
        assertEquals(2350, state.vehicleStats!!.avgRpm)

        val sessions = (state.sessionList as SessionListState.Loaded).sessions
        assertEquals(9, sessions.size)
        assertTrue(sessions.last().durationSeconds < 0)
        assertTrue(sessions.dropLast(1).all { it.durationSeconds >= 0 })
    }

    @Test
    fun `startMockCreateSession resolves the ongoing session and appends a new one`() {
        viewModel.startMockSessions()

        viewModel.startMockCreateSession()

        val sessions = (viewModel.uiState.value.sessionList as SessionListState.Loaded).sessions
        assertEquals(10, sessions.size)
        assertTrue(sessions.dropLast(1).all { it.durationSeconds >= 0 })
        assertEquals(10, sessions.last().id)
        assertTrue(sessions.last().durationSeconds < 0)
    }

    @Test
    fun `startMockEndSession resolves every ongoing session to a non-negative duration`() {
        viewModel.startMockSessions()

        viewModel.startMockEndSession()

        val sessions = (viewModel.uiState.value.sessionList as SessionListState.Loaded).sessions
        assertTrue(sessions.all { it.durationSeconds >= 0 })
        assertTrue(viewModel.uiState.value.actionState is AsyncState.Idle)
    }

    @Test
    fun `startMockSessionStats derives stats deterministically from the session id`() {
        viewModel.startMockSessionStats(4)

        val stats = (viewModel.uiState.value.sessionStats as SessionStatsState.Loaded)
        assertEquals(4, stats.sessionId)
        assertEquals(2300, stats.stats.avgRpm) // 2100 + 4*50
        assertEquals(5200, stats.stats.maxRpm) // 4800 + 4*100
        assertEquals(87f, stats.stats.avgClt, 0.001f) // 85 + 4*0.5
        assertEquals(122f, stats.stats.maxVss, 0.001f) // 110 + 4*3
    }
}
