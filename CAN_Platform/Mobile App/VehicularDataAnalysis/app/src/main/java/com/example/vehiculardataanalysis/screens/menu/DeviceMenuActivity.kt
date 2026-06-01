package com.example.vehiculardataanalysis.screens.menu


import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.compose.setContent
import androidx.compose.runtime.collectAsState
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.example.bleapp.ui.menu.DeviceMenuScreen
import com.example.bleapp.ui.menu.MenuScreen
import com.example.vehiculardataanalysis.DependencyContainer
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.about.AboutActivity
import com.example.vehiculardataanalysis.screens.display.DataDisplayActivity
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class DeviceMenuActivity : BaseActivity() {

    companion object {
        private const val TAG = "DeviceMenuActivity"
        private const val PERMISSION_REQUEST_CODE = 1003
    }

    private var deviceAddress = "Unknown"
    private var deviceName = "Unknown Device"
    private var viewModel: BleViewModel? = null
    private var adapter: android.bluetooth.BluetoothAdapter? = null

    @SuppressLint("MissingPermission")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        deviceAddress = intent.getStringExtra("DEVICE_ADDRESS") ?: "Unknown"
        deviceName = intent.getStringExtra("DEVICE_NAME") ?: "Unknown Device"

        val bluetoothManager =
            getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        adapter = bluetoothManager.adapter

        val container = applicationContext as DependencyContainer
        val factory = container.bleViewModelFactory
        viewModel =
            ViewModelProvider(this, factory)[BleViewModel::class.java]

        // Check permissions before setting content
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

    @SuppressLint("MissingPermission")
    private fun showMenu() {
        // Start scanning for devices
        viewModel?.start(adapter!!)

        setContent {
            VehicularDataAnalysisTheme {
                // Observe scanned devices from repository
                val container = applicationContext as DependencyContainer
                val repository = container.bleRepository
                val scannedDevices = repository.scannedDevices.collectAsState(initial = emptyList()).value

                DeviceMenuScreen(
                    deviceAddress = deviceAddress,
                    deviceName = deviceName,
                    viewModel = viewModel!!,
                    adapter = adapter!!,
                    scannedDevices = scannedDevices,
                    onBackPressed = { finish() },
                    onLiveDataSelected = {
                        navigate<DataDisplayActivity> {
                            it.putExtra("DEVICE_ADDRESS", deviceAddress)
                            it.putExtra("DEVICE_NAME", deviceName)
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