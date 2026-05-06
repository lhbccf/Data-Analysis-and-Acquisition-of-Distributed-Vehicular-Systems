package com.example.vehiculardataanalysis.ui

import androidx.activity.compose.setContent
import androidx.compose.runtime.Composable

abstract class BaseViewModelActivity<T> : BaseActivity() where T : BaseViewModel {
    protected abstract val viewModel: T
    protected fun extendedSetContent(content: @Composable () -> Unit) {
        setContent {
            content()
        }
    }
}