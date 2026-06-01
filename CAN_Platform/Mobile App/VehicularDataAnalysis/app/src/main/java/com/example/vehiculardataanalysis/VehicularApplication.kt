package com.example.vehiculardataanalysis

import android.app.Application
import com.example.bleapp.data.BleManager
import com.example.vehiculardataanalysis.screens.data.BleRepository
import com.example.vehiculardataanalysis.screens.viewmodel.BleViewModelFactory

interface DependencyContainer {
    val bleManager: BleManager
    val bleRepository: BleRepository
    val bleViewModelFactory: BleViewModelFactory
}


class VehicularApplication : Application(), DependencyContainer {

    // Lazy initialization - created only once
    override val bleManager: BleManager by lazy {
        BleManager(this)
    }

    override val bleRepository: BleRepository by lazy {
        BleRepository(bleManager)
    }

    override val bleViewModelFactory: BleViewModelFactory by lazy {
        BleViewModelFactory(bleRepository)
    }
}