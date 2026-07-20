package com.example.vehiculardataanalysis.domain

data class DeviceUi(
    val name: String,
    val mac: String,
    val tags: List<String>,
    val isPairedOnly: Boolean = false
)

data class Device(
    val name: String,
    val address: String,
    val isPairedOnly: Boolean = false
)