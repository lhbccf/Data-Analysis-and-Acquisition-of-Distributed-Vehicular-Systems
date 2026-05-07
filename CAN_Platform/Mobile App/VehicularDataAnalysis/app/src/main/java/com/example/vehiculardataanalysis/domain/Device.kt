package com.example.vehiculardataanalysis.domain

data class DeviceUi(
    val name: String,
    val mac: String,
    val tags: List<String>
)

data class Device(
    val name: String,
    val address: String
)