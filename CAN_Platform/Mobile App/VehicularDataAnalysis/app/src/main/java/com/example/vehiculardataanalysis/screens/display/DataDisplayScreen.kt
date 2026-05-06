package com.example.vehiculardataanalysis.screens.display

import android.bluetooth.BluetoothManager
import android.content.Context
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalContext
import com.example.vehiculardataanalysis.components.DeviceSection
import com.example.vehiculardataanalysis.components.SignalSection
import com.example.vehiculardataanalysis.domain.DeviceUi

@Composable
fun MainScreen(viewModel: DataDisplayViewModel) {

    val state by viewModel.uiState.collectAsState()

    val context = LocalContext.current
    val bluetoothManager =
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    val adapter = bluetoothManager.adapter

    Column {

        Button(onClick = { viewModel.start(adapter) }) {
            Text("Connect")
        }

        DeviceSection(
            devices = listOf(
                DeviceUi(
                    name = "MyPiBLE",
                    mac = "C7:30:...",
                    tags = listOf("CAN", "BLE")
                )
            ),
            onClick = {}
        )

        SignalSection(
            title = "RPM",
            value = state.rpm.toFloat(),
            range = 0f..9000f,
            unit = "RPM"
        )
    }
}