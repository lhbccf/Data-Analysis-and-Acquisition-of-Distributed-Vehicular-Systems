package com.example.vehiculardataanalysis.screens.menu


import android.annotation.SuppressLint
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.ViewModelProvider
import com.example.bleapp.data.BleManager
import com.example.bleapp.ui.menu.MenuScreen
import com.example.vehiculardataanalysis.MainScreen
import com.example.vehiculardataanalysis.domain.Device
import com.example.vehiculardataanalysis.screens.about.AboutActivity
import com.example.vehiculardataanalysis.screens.data.BleRepository
import com.example.vehiculardataanalysis.screens.display.DataDisplayActivity
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModel
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModelFactory
import com.example.vehiculardataanalysis.screens.viewmodel.DeviceViewModel
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class MenuActivity : BaseActivity() {

    @SuppressLint("MissingPermission")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        //val address = intent.getStringExtra("DEVICE_ADDRESS") ?: return

        val bluetoothManager =
            getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        val adapter = bluetoothManager.adapter

        val manager = BleManager(this)
        val repo = BleRepository(manager)

        val factory = BleViewModelFactory(repo)
        val viewModel =
            ViewModelProvider(this, factory)[BleViewModel::class.java]

        val device = Device("Selected Device", "TEST")

        //viewModel.connect(device)

        setContent {
            VehicularDataAnalysisTheme {
                MainScreen(viewModel, adapter,
                    onDeviceSelected = { navigate<DataDisplayActivity>() },
                    onAboutRequested = { navigate<AboutActivity>() })
            }
        }
    }
}