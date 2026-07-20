package com.example.vehiculardataanalysis.screens.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.vehiculardataanalysis.screens.data.BleRepository

class BleViewModelFactory(
    private val repository: BleRepository
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T = when {
        modelClass.isAssignableFrom(BleViewModel::class.java) ->
            BleViewModel(repository) as T
        modelClass.isAssignableFrom(SessionViewModel::class.java) ->
            SessionViewModel(repository) as T
        else -> throw IllegalArgumentException("Unknown ViewModel: ${modelClass.name}")
    }
}
