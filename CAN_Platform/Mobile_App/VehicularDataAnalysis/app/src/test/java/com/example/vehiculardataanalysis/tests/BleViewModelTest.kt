package com.example.vehiculardataanalysis.tests

import android.bluetooth.BluetoothAdapter
import com.example.vehiculardataanalysis.screens.data.BleRepository
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import io.mockk.mockk
import io.mockk.every
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/**
 * BleViewModel turns raw CSV lines streamed from the vehicle's BLE device into MainUiState.
 * The device is an untrusted external source (dropped bytes, truncated frames, noise), so
 * the parser's fallback-to-default behavior is the important contract to lock down here.
 */
class BleViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var repository: BleRepository
    private lateinit var canData: MutableSharedFlow<String>
    private lateinit var viewModel: BleViewModel

    private val timeoutMs = 2_000L

    @Before
    fun setUp() {
        canData = MutableSharedFlow(extraBufferCapacity = 64)
        repository = mockk(relaxed = true)
        every { repository.canData } returns canData

        viewModel = BleViewModel(repository)
        viewModel.start(mockk<BluetoothAdapter>())
    }

    private suspend fun emit(line: String) {
        canData.subscriptionCount.first { it > 0 }
        canData.emit(line)
    }

    @Test
    fun `full CAN line maps every field in order`() = runBlocking {
        val line = "2500,88.5,14.2,25.0,55.0,12.6,5.2,15.0,45.0,30.0,100.0,60.0,1"
        emit(line)

        val s = withTimeout(timeoutMs) { viewModel.uiState.first { it.rpm == 2500 } }

        assertEquals(2500, s.rpm)
        assertEquals(88.5f, s.temp, 0.0001f)
        assertEquals(14.2f, s.afr, 0.0001f)
        assertEquals(25.0f, s.tps, 0.0001f)
        assertEquals(55.0f, s.map, 0.0001f)
        assertEquals(12.6f, s.battery, 0.0001f)
        assertEquals(5.2f, s.dwell, 0.0001f)
        assertEquals(15.0f, s.timing, 0.0001f)
        assertEquals(45.0f, s.vss, 0.0001f)
        assertEquals(30.0f, s.iat, 0.0001f)
        assertEquals(100.0f, s.ego_cor, 0.0001f)
        assertEquals(60.0f, s.ve, 0.0001f)
        assertEquals(1, s.sync)
        assertEquals(line, s.raw)
    }

    @Test
    fun `missing trailing fields default to zero instead of crashing`() = runBlocking {
        emit("3000,90.0")

        val s = withTimeout(timeoutMs) { viewModel.uiState.first { it.rpm == 3000 } }

        assertEquals(90.0f, s.temp, 0.0001f)
        assertEquals(0f, s.afr, 0.0001f)
        assertEquals(0, s.sync)
    }

    @Test
    fun `non-numeric fields fall back to zero without crashing the collector`() = runBlocking {
        emit("abc,def,14.2,ghi")

        val s = withTimeout(timeoutMs) { viewModel.uiState.first { it.raw == "abc,def,14.2,ghi" } }

        assertEquals(0, s.rpm)
        assertEquals(0f, s.temp, 0.0001f)
        assertEquals(14.2f, s.afr, 0.0001f)
        assertEquals(0f, s.tps, 0.0001f)
    }

    @Test
    fun `whitespace around values is trimmed but the raw line is preserved verbatim`() = runBlocking {
        val line = " 4000 , 91.2 , 14.7 "
        emit(line)

        val s = withTimeout(timeoutMs) { viewModel.uiState.first { it.rpm == 4000 } }

        assertEquals(91.2f, s.temp, 0.0001f)
        assertEquals(14.7f, s.afr, 0.0001f)
        assertEquals(line, s.raw)
    }

    @Test
    fun `blank line is ignored and does not overwrite the previous reading`() = runBlocking {
        emit("1500,75.0,14.0")
        withTimeout(timeoutMs) { viewModel.uiState.first { it.rpm == 1500 } }

        emit("")
        emit("2200,80.0,14.5")

        val s = withTimeout(timeoutMs) { viewModel.uiState.first { it.rpm == 2200 } }
        assertEquals(80.0f, s.temp, 0.0001f)
    }
}
