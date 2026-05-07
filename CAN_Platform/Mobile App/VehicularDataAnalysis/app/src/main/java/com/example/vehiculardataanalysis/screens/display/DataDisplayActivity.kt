package com.example.vehiculardataanalysis.screens.display

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.example.vehiculardataanalysis.ui.BaseActivity
import com.example.vehiculardataanalysis.ui.theme.VehicularDataAnalysisTheme

class DataDisplayActivity: BaseActivity(){
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            VehicularDataAnalysisTheme {
                DataDisplayScreen()
            }
        }
    }

    override fun backPressed() {
        finish()
    }
}

@Preview(showBackground = true)
@Composable
fun DataPreview() {
    VehicularDataAnalysisTheme {
        DataDisplayScreen()
    }
}
