package com.example.vehiculardataanalysis.screens.display

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.components.SignalTile
import com.example.vehiculardataanalysis.components.SyncTile
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import com.example.vehiculardataanalysis.screens.viewmodel.MainUiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DataDisplayScreen(
    deviceAddress: String = "Unknown",
    deviceName: String = "Unknown Device",
    viewModel: BleViewModel? = null,
    isTestDevice: Boolean = false,
    onBackPressed: () -> Unit = {}
) {
    val state = viewModel?.uiState?.collectAsState()?.value ?: MainUiState()

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                navigationIcon = {
                    IconButton(onClick = onBackPressed) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = MaterialTheme.colorScheme.onSurface
                        )
                    }
                },
                title = {
                    Text(
                        "$deviceName${if (isTestDevice) " (Mock)" else ""} — Live Data",
                        fontSize = 20.sp
                    )
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface,
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 4.dp, vertical = 4.dp)
        ) {
            SignalTile(
                label = "RPM", value = state.rpm.toFloat(),
                range = 0f..6500f, unit = "rpm", format = "%.0f",
                warnFraction = 0.538f, dangerFraction = 0.615f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "SPEED", value = state.vss,
                range = 0f..250f, unit = "km/h", format = "%.0f",
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "THROTTLE", value = state.tps,
                range = 0f..100f, unit = "%", format = "%.1f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "MAP", value = state.map,
                range = 0f..300f, unit = "kPa", format = "%.0f",
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "AIR/FUEL", value = state.afr,
                range = 10f..20f, unit = "λ", format = "%.2f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "BATTERY", value = state.battery,
                range = 8f..18f, unit = "V", format = "%.1f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "DWELL", value = state.dwell,
                range = 0f..8f, unit = "ms", format = "%.1f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "IGNITION", value = state.timing,
                range = 0f..45f, unit = "°", format = "%.1f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "INTAKE TEMP", value = state.iat,
                range = -40f..120f, unit = "°C", format = "%.0f",
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "O2 TRIM", value = state.ego_cor,
                range = 70f..130f, unit = "%", format = "%.1f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SignalTile(
                label = "VOL. EFF.", value = state.ve,
                range = 0f..120f, unit = "%", format = "%.0f",
                warnFraction = 1.1f, dangerFraction = 1.1f,
                modifier = Modifier.fillMaxWidth()
            )
            SyncTile(
                synced = state.sync == 1,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
