package com.example.vehiculardataanalysis.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.unit.dp

@Composable
fun DeviceCard(
    name: String,
    mac: String,
    tags: List<String>,
    enabled: Boolean = true,
    onClick: () -> Unit
) {
    val modifier = Modifier
        .fillMaxWidth()
        .padding(vertical = 6.dp)
    val colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceVariant
    )
    val shape = RoundedCornerShape(16.dp)
    val content: @Composable () -> Unit = {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = name, color = MaterialTheme.colorScheme.onSurface)
            Text(
                text = mac,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface
            )
            Row(modifier = Modifier.padding(top = 8.dp)) {
                tags.forEach { tag ->
                    AssistChip(
                        onClick = {},
                        label = { Text(tag) },
                        modifier = Modifier.padding(end = 6.dp)
                    )
                }
            }
        }
    }

    if (enabled) {
        Card(onClick = onClick, modifier = modifier, colors = colors, shape = shape) { content() }
    } else {
        Card(modifier = modifier.alpha(0.4f), colors = colors, shape = shape) { content() }
    }
}
