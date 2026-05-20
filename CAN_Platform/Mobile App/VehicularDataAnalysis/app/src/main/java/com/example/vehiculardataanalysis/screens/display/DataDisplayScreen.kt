package com.example.vehiculardataanalysis.screens.display

import android.bluetooth.BluetoothAdapter
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.R
import com.example.vehiculardataanalysis.components.DeviceSection
import com.example.vehiculardataanalysis.components.SignalSection
import com.example.vehiculardataanalysis.domain.DeviceUi
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import com.example.vehiculardataanalysis.screens.viewmodel.MainUiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DataDisplayScreen (
    deviceAddress: String = "Unknown",
    deviceName: String = "Unknown Device",
    viewModel: BleViewModel? = null,
    isTestDevice: Boolean = false
){
    val state = viewModel?.uiState?.collectAsState()?.value
        ?: MainUiState()

    Scaffold(modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("$deviceName${if(isTestDevice) " (Mock)" else ""} - Live Data", fontSize = 20.sp) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface,
                )
            )}) { innerPadding ->
        Column(modifier = Modifier
            .padding(innerPadding)
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally)
        {

            SignalSection(
                title = "RPM",
                value = state.rpm.toFloat(),
                range = 0f..9000f,
                unit = "RPM"
            )
            SignalSection(
                title = "Coolant",
                value = state.temp,
                range = -40f..140f,
                unit = "ºC"
            )
            SignalSection(
                title = "TPS",
                value = state.tps,
                range = 0f..100f,
                unit = "V"
            )
            SignalSection(
                title = "MAP",
                value = state.map,
                range = 0f..300f,
                unit = "Pressure"
            )
            SignalSection(
                title = "Air-Fuel Ratio",
                value = state.afr,
                range = 10f..20f,
                unit = "Ratio"
            )
            SignalSection(
                title = "Battery",
                value = state.battery,
                range = 8f..18f,
                unit = "Ah"
            )
            SignalSection(
                title = "Dwell",
                value = state.dwell,
                range = 0f..180f,
                unit = "º"
            )
            SignalSection(
                title = "Timing",
                value = state.timing,
                range = 0f..180f,
                unit = "º"
            )
            
            Text(
                text = "Raw Data: ${state.raw}",
                modifier = Modifier.padding(16.dp),
                color = MaterialTheme.colorScheme.onSurface,
                fontSize = 8.sp
            )
        }
    }
}