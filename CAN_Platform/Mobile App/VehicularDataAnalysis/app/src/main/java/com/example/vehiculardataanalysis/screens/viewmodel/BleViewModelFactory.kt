package com.example.vehiculardataanalysis.screens.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.vehiculardataanalysis.screens.data.BleRepository

class BleViewModelFactory(
    private val repository: BleRepository
) : ViewModelProvider.Factory {

    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return BleViewModel(repository) as T
    }
}