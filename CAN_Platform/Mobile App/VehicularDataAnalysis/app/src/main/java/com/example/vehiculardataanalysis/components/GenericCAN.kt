package com.example.vehiculardataanalysis.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp



/**
 * Compact two-per-row signal tile used in the live data screen.
 *
 * @param warnFraction   Fraction of range at which the bar/value turns orange (default 0.75).
 * @param dangerFraction Fraction at which it turns red (default 0.90).
 */
@Composable
fun SignalTile(
    label: String,
    value: Float,
    range: ClosedFloatingPointRange<Float>,
    unit: String,
    format: String = "%.1f",
    warnFraction: Float = 1f,
    dangerFraction: Float = 1f,
    modifier: Modifier = Modifier,
) {
    val span     = range.endInclusive - range.start
    val fraction = if (span > 0f) ((value - range.start) / span).coerceIn(0f, 1f) else 0f
    val display  = remember(value, format) { format.format(value) }

    val accent = when {
        fraction >= dangerFraction -> MaterialTheme.colorScheme.error
        fraction >= warnFraction   -> MaterialTheme.colorScheme.tertiary
        else                       -> MaterialTheme.colorScheme.primary
    }

    val rangeStart = remember(range.start) {
        if (range.start == range.start.toLong().toFloat()) "${range.start.toLong()}"
        else "%.1f".format(range.start)
    }
    val rangeEnd = remember(range.endInclusive) {
        if (range.endInclusive == range.endInclusive.toLong().toFloat()) "${range.endInclusive.toLong()}"
        else "%.1f".format(range.endInclusive)
    }

    Card(
        modifier = modifier.padding(4.dp),
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.55f),
                    letterSpacing = 1.2.sp,
                )
                Text(
                    text = "$display $unit",
                    fontFamily = FontFamily.Monospace,
                    fontSize = 13.sp,
                    color = accent,
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            // Progress track
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(2.dp))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(fraction)
                        .height(4.dp)
                        .background(accent, RoundedCornerShape(2.dp))
                )
            }
            Spacer(modifier = Modifier.height(3.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(rangeStart, fontSize = 9.sp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.30f))
                Text(rangeEnd,   fontSize = 9.sp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.30f))
            }
        }
    }
}

/**
 * Boolean sync-status tile — shows LOCKED (green) or NO SYNC (red).
 */
@Composable
fun SyncTile(synced: Boolean, modifier: Modifier = Modifier) {
    val color = if (synced) MaterialTheme.colorScheme.onTertiary else MaterialTheme.colorScheme.error
    val label = if (synced) "LOCKED" else "NO SYNC"

    Card(
        modifier = modifier.padding(4.dp),
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "SYNC",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.55f),
                    letterSpacing = 1.2.sp,
                )
                Text(
                    text = label,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 13.sp,
                    color = color,
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .background(if (synced) color else MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(2.dp))
            )
            Spacer(modifier = Modifier.height(12.dp))
        }
    }
}
