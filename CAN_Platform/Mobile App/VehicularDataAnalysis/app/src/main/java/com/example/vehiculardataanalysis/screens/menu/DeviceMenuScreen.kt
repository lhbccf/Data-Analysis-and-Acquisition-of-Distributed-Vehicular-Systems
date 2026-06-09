package com.example.bleapp.ui.menu

import android.bluetooth.BluetoothAdapter
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.components.ButtonOption
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DeviceMenuScreen(
    deviceAddress: String = "Unknown",
    deviceName: String = "Unknown Device",
    viewModel: BleViewModel,
    adapter: BluetoothAdapter,
    scannedDevices: List<Device> = emptyList(),
    onBackPressed: () -> Unit,
    onLiveDataSelected: () -> Unit,
    onSessionsSelected: () -> Unit,
) {

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(deviceName, fontSize = 24.sp) },
                navigationIcon = {
                    IconButton(onClick = onBackPressed) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Localized description"
                        )
                    }
                },
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
                .padding(16.dp)
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState())
        ) {


            Text(
                text = "Device Options",
                style = MaterialTheme.typography.titleLarge
            )

            Spacer(modifier = Modifier.height(8.dp))

            ButtonOption("Live Data", onClick = onLiveDataSelected)
            ButtonOption("Sessions Information", onClick = onSessionsSelected)
            ButtonOption("Overall Statistics", onClick = {})
            ButtonOption("Device Information", onClick = {})

        }
    }
}