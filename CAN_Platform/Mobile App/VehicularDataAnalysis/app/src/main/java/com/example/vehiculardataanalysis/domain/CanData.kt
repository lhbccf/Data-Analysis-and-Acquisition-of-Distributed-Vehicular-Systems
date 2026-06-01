package com.example.vehiculardataanalysis.domain

data class CanData(
    val rpm: Int? = null,
    val temp: Float? = null,
    val afr: Float? = null,
    val raw: String = ""
)