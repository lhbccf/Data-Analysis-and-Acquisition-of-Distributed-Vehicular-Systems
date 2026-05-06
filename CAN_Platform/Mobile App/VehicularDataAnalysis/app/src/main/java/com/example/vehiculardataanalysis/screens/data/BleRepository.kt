package com.example.vehiculardataanalysis.screens.data

import com.example.vehiculardataanalysis.domain.CanData
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class BleRepository(private val bleManager: BleManager) {

    val canData: Flow<CanData> = bleManager.dataFlow.map { raw ->
        parse(raw)
    }

    private fun parse(raw: String): CanData {
        // Example: "RPM:3000|TEMP:90|AFR:14.7"
        val parts = raw.split("|")

        var rpm: Int? = null
        var temp: Float? = null
        var afr: Float? = null

        parts.forEach {
            val kv = it.split(":")
            if (kv.size == 2) {
                when (kv[0]) {
                    "RPM" -> rpm = kv[1].toIntOrNull()
                    "TEMP" -> temp = kv[1].toFloatOrNull()
                    "AFR" -> afr = kv[1].toFloatOrNull()
                }
            }
        }

        return CanData(rpm, temp, afr, raw)
    }

    fun start(adapter: android.bluetooth.BluetoothAdapter) {
        bleManager.startScan(adapter)
    }
}