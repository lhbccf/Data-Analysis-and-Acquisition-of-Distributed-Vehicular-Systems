package com.example.bleapp.ui.menu

import android.bluetooth.BluetoothAdapter
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
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
fun MenuScreen(
    viewModel: BleViewModel,
    adapter: BluetoothAdapter,
    scannedDevices: List<Device> = emptyList(),
    onDeviceSelected: (DeviceUi) -> Unit,
    onAboutRequested: () -> Unit
) {

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(stringResource(R.string.app_name), fontSize = 24.sp) },
                actions = {
                    IconButton(onClick = onAboutRequested) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = "Information"
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
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            // Test Device option
            val testDeviceUi = DeviceUi(
                name = "Test Device",
                mac = "AA:BB:CC:DD:EE:FF",
                tags = listOf("Mock")
            )

            // Convert scanned Device objects to DeviceUi for display
            val deviceUiList = mutableListOf(testDeviceUi)

            scannedDevices.forEach { device ->
                deviceUiList.add(
                    DeviceUi(
                        name = device.name,
                        mac = device.address,
                        tags = listOf("BLE")
                    )
                )
            }


            DeviceSection(
                devices = deviceUiList,
                onClick = onDeviceSelected
            )

        }
    }
}