package com.example.bleapp.ui.menu

import android.bluetooth.BluetoothAdapter
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.R
import com.example.vehiculardataanalysis.components.DeviceSection
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.domain.DeviceUi
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DeviceMenuScreen(
    deviceAddress: String = "Unknown",
    deviceName: String = "Unknown Device",
    viewModel: BleViewModel,
    adapter: BluetoothAdapter,
    scannedDevices: List<Device> = emptyList(),
    onLiveDataSelected: () -> Unit,
) {

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(deviceName, fontSize = 28.sp) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface,
                )
            )
        }) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {


            Button(
                modifier = Modifier
                    .padding(innerPadding),
                onClick = onLiveDataSelected
            ) {
                Text("Live Data")
            }
        }
    }
}