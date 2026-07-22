package com.example.vehiculardataanalysis.screens.display

import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.compose.setContent
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.example.vehiculardataanalysis.DependencyContainer
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import com.example.vehiculardataanalysis.screens.viewmodel.SessionViewModel
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class SessionStatsActivity : BaseActivity() {

    companion object {
        private const val TAG = "SessionStatsActivity"
        private const val PERMISSION_REQUEST_CODE = 1006
        private const val TEST_DEVICE_MAC = "AA:BB:CC:DD:EE:FF"
    }

    private var deviceAddress = "Unknown"
    private var deviceName = "Unknown Device"
    private var isTestDevice = false
    private var sessionId = -1
    private var sessionStart = 0.0
    private var sessionDuration = 0.0
    private var bleViewModel: BleViewModel? = null
    private var sessionViewModel: SessionViewModel? = null

    @SuppressLint("MissingPermission")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        deviceAddress    = intent.getStringExtra("DEVICE_ADDRESS") ?: "Unknown"
        deviceName       = intent.getStringExtra("DEVICE_NAME") ?: "Unknown Device"
        sessionId        = intent.getIntExtra("SESSION_ID", -1)
        sessionStart     = intent.getDoubleExtra("SESSION_START", 0.0)
        sessionDuration  = intent.getDoubleExtra("SESSION_DURATION", 0.0)
        isTestDevice     = deviceAddress == TEST_DEVICE_MAC

        val container = applicationContext as DependencyContainer
        val factory   = container.bleViewModelFactory
        bleViewModel    = ViewModelProvider(this, factory)[BleViewModel::class.java]
        sessionViewModel = ViewModelProvider(this, factory)[SessionViewModel::class.java]

        if (hasBluetoothPermissions()) {
            connectAndShow()
        } else {
            requestBluetoothPermissions()
        }
    }

    private fun hasBluetoothPermissions(): Boolean =
        ContextCompat.checkSelfPermission(
            this, Manifest.permission.BLUETOOTH_CONNECT
        ) == PackageManager.PERMISSION_GRANTED

    private fun requestBluetoothPermissions() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.ACCESS_FINE_LOCATION
            ),
            PERMISSION_REQUEST_CODE
        )
    }

    @SuppressLint("MissingPermission")
    private fun connectAndShow() {
        if (isTestDevice) {
            sessionViewModel?.startMockSessionStats(sessionId)
        } else {
            bleViewModel?.connect(Device(deviceName, deviceAddress))
            sessionViewModel?.requestSessionStats(sessionId)
        }

        setContent {
            VehicularDataAnalysisTheme {
                SessionStatsScreen(
                    sessionId               = sessionId,
                    sessionStartEpoch       = sessionStart,
                    sessionDurationSeconds  = sessionDuration,
                    deviceName              = deviceName,
                    isTestDevice            = isTestDevice,
                    sessionViewModel        = sessionViewModel!!,
                    onBackPressed           = { finish() },
                    onRetry                 = {
                        if (isTestDevice) sessionViewModel?.startMockSessionStats(sessionId)
                        else sessionViewModel?.requestSessionStats(sessionId)
                    }
                )
            }
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE &&
            grantResults.isNotEmpty() &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED
        ) {
            connectAndShow()
        } else {
            Log.e(TAG, "Bluetooth permissions denied")
            finish()
        }
    }

    override fun backPressed() = finish()
}
