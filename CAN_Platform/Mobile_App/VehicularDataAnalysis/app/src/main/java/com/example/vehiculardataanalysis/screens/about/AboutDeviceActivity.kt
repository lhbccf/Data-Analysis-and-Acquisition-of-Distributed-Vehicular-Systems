package com.example.vehiculardataanalysis.screens.about

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import com.example.vehiculardataanalysis.DependencyContainer
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme
import kotlinx.coroutines.flow.map

class AboutDeviceActivity : BaseActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val deviceAddress = intent.getStringExtra("DEVICE_ADDRESS") ?: "Unknown"
        val deviceName = intent.getStringExtra("DEVICE_NAME") ?: "Unknown Device"
        val connectedSinceMs = intent.getLongExtra("CONNECTED_SINCE_MS", System.currentTimeMillis())

        val repository = (applicationContext as DependencyContainer).bleRepository

        setContent {
            VehicularDataAnalysisTheme {
                val lastDataReceivedMs by repository.canData
                    .map { System.currentTimeMillis() }
                    .collectAsState(initial = 0L)

                AboutDeviceScreen(
                    deviceName = deviceName,
                    deviceAddress = deviceAddress,
                    connectedSinceMs = connectedSinceMs,
                    lastDataReceivedMs = lastDataReceivedMs,
                    onBackPressed = { finish() }
                )
            }
        }
    }

    override fun backPressed() {
        finish()
    }
}
