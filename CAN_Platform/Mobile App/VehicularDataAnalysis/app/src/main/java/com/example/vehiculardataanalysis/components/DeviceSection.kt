package com.example.vehiculardataanalysis.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.vehiculardataanalysis.domain.DeviceUi

@Composable
fun DeviceSection(devices: List<DeviceUi>, onClick: (DeviceUi) -> Unit) {
    Column(modifier = Modifier.padding(16.dp)) {

        Text(
            text = "Connected Devices",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(8.dp))

        devices.forEach {
            DeviceCard(
                name = it.name,
                mac = it.mac,
                tags = it.tags,
                onClick = { onClick(it) }
            )
        }
    }
}