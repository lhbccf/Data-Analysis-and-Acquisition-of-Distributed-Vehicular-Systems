package com.example.vehiculardataanalysis.screens.menu


import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.compose.setContent
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.bleapp.ui.menu.DeviceMenuScreen
import com.example.vehiculardataanalysis.screens.about.AboutDeviceActivity
import com.example.vehiculardataanalysis.screens.display.DataDisplayActivity
import com.example.vehiculardataanalysis.screens.display.OverallStatsActivity
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class DeviceMenuActivity : BaseActivity() {

    companion object {
        private const val TAG = "DeviceMenuActivity"
        private const val PERMISSION_REQUEST_CODE = 1003
    }

    private var deviceAddress = "Unknown"
    private var deviceName = "Unknown Device"
    private var connectionTimeMs: Long = 0L

    @SuppressLint("MissingPermission")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        deviceAddress = intent.getStringExtra("DEVICE_ADDRESS") ?: "Unknown"
        deviceName = intent.getStringExtra("DEVICE_NAME") ?: "Unknown Device"
        connectionTimeMs = System.currentTimeMillis()

        if (hasBluetoothPermissions()) {
            showMenu()
        } else {
            requestBluetoothPermissions()
        }
    }

    private fun hasBluetoothPermissions(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.BLUETOOTH_SCAN
        ) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.BLUETOOTH_CONNECT
                ) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestBluetoothPermissions() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.ACCESS_FINE_LOCATION
            ),
            PERMISSION_REQUEST_CODE
        )
    }

    private fun showMenu() {
        setContent {
            VehicularDataAnalysisTheme {
                DeviceMenuScreen(
                    deviceAddress = deviceAddress,
                    deviceName = deviceName,
                    onBackPressed = { finish() },
                    onLiveDataSelected = {
                        navigate<DataDisplayActivity> {
                            it.putExtra("DEVICE_ADDRESS", deviceAddress)
                            it.putExtra("DEVICE_NAME", deviceName)
                        }
                    },
                    onSessionsSelected = {
                        navigate<SessionMenuActivity> {
                            it.putExtra("DEVICE_ADDRESS", deviceAddress)
                            it.putExtra("DEVICE_NAME", deviceName)
                        }
                    },
                    onOverallStatsSelected = {
                        navigate<OverallStatsActivity> {
                            it.putExtra("DEVICE_ADDRESS", deviceAddress)
                            it.putExtra("DEVICE_NAME", deviceName)
                        }
                    },
                    onDeviceInfoSelected = {
                        navigate<AboutDeviceActivity> {
                            it.putExtra("DEVICE_ADDRESS", deviceAddress)
                            it.putExtra("DEVICE_NAME", deviceName)
                            it.putExtra("CONNECTED_SINCE_MS", connectionTimeMs)
                        }
                    },
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

        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() &&
                grantResults[0] == PackageManager.PERMISSION_GRANTED &&
                grantResults[1] == PackageManager.PERMISSION_GRANTED
            ) {
                Log.d(TAG, "Bluetooth permissions granted")
                showMenu()
            } else {
                Log.e(TAG, "Bluetooth permissions denied")
                finish()
            }
        }
    }

    override fun backPressed() {
        finish()
    }
}