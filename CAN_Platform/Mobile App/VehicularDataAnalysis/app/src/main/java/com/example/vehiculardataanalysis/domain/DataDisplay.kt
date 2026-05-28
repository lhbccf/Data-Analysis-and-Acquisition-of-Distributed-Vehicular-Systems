package com.example.vehiculardataanalysis.domain

import androidx.lifecycle.viewmodel.CreationExtras

enum class SectionState(val value: String){
    ERROR("Error"),
    EMPTY("Empty"),
    LOADING("Loading"),
    ON("On")
}

class Section(
    val pos: Int,
    val state: SectionState
)

class DisplayState(
    val sections: Array<Section>,
)

class Display(){
    val displays: Array<Section> = buildDisplay()

    companion object {
        const val SECTION_SIZE = 8

        private fun buildDisplay(): Array<Section> {
            val list = MutableList(SECTION_SIZE){
                Section(it, SectionState.EMPTY)
            }
            return list.toTypedArray()
        }
    }
}


class DataDisplay {
    companion object {
        const val SECTION_SIZE = 8
    }

    private val displayState = Display()
}