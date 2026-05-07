package com.example.bleapp.ui.menu

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
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
    onDeviceSelected: (DeviceUi) -> Unit,
    onAboutRequested: () -> Unit
) {

    val state by viewModel.uiState.collectAsState()

    val context = LocalContext.current
    val bluetoothManager =
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(stringResource(R.string.app_name), fontSize = 28.sp) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface,
                )
            )
        }) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.background),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {


            DeviceSection(
                devices = listOf(
                    DeviceUi(
                        name = "MyPiBLE",
                        mac = "C7:30:...",
                        tags = listOf("CAN", "BLE")
                    ),
                    DeviceUi(
                        name = "MyPiBLE2",
                        mac = "M3:45:...",
                        tags = listOf("CAN", "BLE")
                    ),
                    DeviceUi(
                        name = "MyPiBLE3",
                        mac = "RR:54:...",
                        tags = listOf("CAN", "BLE")
                    )

                ),
                onClick = onDeviceSelected
            )

            Button(
                modifier = Modifier
                    .padding(innerPadding),
                onClick = onAboutRequested
            ) {
                Text("About")
            }
        }
    }
}