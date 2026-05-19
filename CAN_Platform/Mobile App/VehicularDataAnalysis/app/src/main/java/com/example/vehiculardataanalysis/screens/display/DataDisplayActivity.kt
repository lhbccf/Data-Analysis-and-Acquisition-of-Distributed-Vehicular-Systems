package com.example.vehiculardataanalysis.screens.display

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.example.vehiculardataanalysis.DependencyContainer
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class DataDisplayActivity: BaseActivity(){

    companion object {
        private const val TAG = "DataDisplayActivity"
        private const val PERMISSION_REQUEST_CODE = 1002
    }

    private var deviceAddress = "Unknown"
    private var deviceName = "Unknown Device"
    private var viewModel: BleViewModel? = null

    @SuppressLint("MissingPermission")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        deviceAddress = intent.getStringExtra("DEVICE_ADDRESS") ?: "Unknown"
        deviceName = intent.getStringExtra("DEVICE_NAME") ?: "Unknown Device"

        val bluetoothManager =
            getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        val adapter = bluetoothManager.adapter

        val container = applicationContext as DependencyContainer
        val factory = container.bleViewModelFactory
        viewModel = ViewModelProvider(this, factory)[BleViewModel::class.java]

        // Check permissions before connecting
        if (hasBluetoothPermissions()) {
            connectAndDisplay(adapter)
        } else {
            requestBluetoothPermissions()
        }
    }

    private fun hasBluetoothPermissions(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.BLUETOOTH_CONNECT
        ) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.BLUETOOTH_SCAN
                ) == PackageManager.PERMISSION_GRANTED
    }

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
    private fun connectAndDisplay(adapter: android.bluetooth.BluetoothAdapter?) {
        if (adapter == null || viewModel == null) {
            Log.e(TAG, "Adapter or ViewModel is null")
            finish()
            return
        }

        /*val device = Device(deviceName, deviceAddress)
        viewModel!!.connect(device)
        viewModel!!.start(adapter)*/

        setContent {
            VehicularDataAnalysisTheme {
                DataDisplayScreen(
                    deviceAddress = deviceAddress,
                    deviceName = deviceName,
                    viewModel = viewModel
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
                val bluetoothManager =
                    getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
                connectAndDisplay(bluetoothManager.adapter)
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

@Preview(showBackground = true)
@Composable
fun DataPreview() {
    VehicularDataAnalysisTheme {
        DataDisplayScreen()
    }
}
