package com.example.bleapp.ui.menu

import android.bluetooth.BluetoothAdapter
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.combinedClickable
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.R
import com.example.vehiculardataanalysis.components.DeviceSection
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.domain.DeviceUi
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun MenuScreen(
    viewModel: BleViewModel,
    adapter: BluetoothAdapter,
    scannedDevices: List<Device> = emptyList(),
    onDeviceSelected: (DeviceUi) -> Unit,
    onAboutRequested: () -> Unit
) {
    // Hidden by default; long-pressing the info button reveals it for testing without a device.
    var showTestDevice by remember { mutableStateOf(false) }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(stringResource(R.string.app_name), fontSize = 24.sp) },
                actions = {
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .combinedClickable(
                                onClick = onAboutRequested,
                                onLongClick = { showTestDevice = !showTestDevice }
                            ),
                        contentAlignment = Alignment.Center
                    ) {
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

            // Convert scanned Device objects to DeviceUi for display
            val deviceUiList = mutableListOf<DeviceUi>()

            if (showTestDevice) {
                deviceUiList.add(
                    DeviceUi(
                        name = "Test Device",
                        mac = "AA:BB:CC:DD:EE:FF",
                        tags = listOf("Mock")
                    )
                )
            }

            scannedDevices.forEach { device ->
                deviceUiList.add(
                    DeviceUi(
                        name = device.name,
                        mac = device.address,
                        tags = if (device.isPairedOnly) listOf("Paired") else listOf("Connected"),
                        isPairedOnly = device.isPairedOnly
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