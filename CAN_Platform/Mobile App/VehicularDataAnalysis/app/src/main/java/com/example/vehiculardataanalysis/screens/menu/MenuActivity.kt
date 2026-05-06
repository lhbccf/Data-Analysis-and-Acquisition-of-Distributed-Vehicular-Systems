package com.example.vehiculardataanalysis.screens.menu

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.example.vehiculardataanalysis.screens.about.AboutActivity
import com.example.vehiculardataanalysis.screens.display.DataDisplayActivity
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class MenuActivity : BaseActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            VehicularDataAnalysisTheme {

            }
        }
    }

    override fun backPressed() {
        finish()
    }
}