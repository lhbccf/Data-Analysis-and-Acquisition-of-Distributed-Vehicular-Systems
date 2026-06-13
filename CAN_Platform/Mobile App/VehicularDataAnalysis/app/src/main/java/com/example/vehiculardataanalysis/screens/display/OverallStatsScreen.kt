package com.example.vehiculardataanalysis.screens.display

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.domain.SessionInfo
import com.example.vehiculardataanalysis.screens.viewmodel.OverallVehicleStats
import com.example.vehiculardataanalysis.screens.viewmodel.SessionListState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionViewModel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OverallStatsScreen(
    deviceName: String = "Unknown Device",
    isTestDevice: Boolean = false,
    sessionViewModel: SessionViewModel,
    onBackPressed: () -> Unit,
    onRefresh: () -> Unit
) {
    val state        = sessionViewModel.state.collectAsState().value
    val vehicleStats = sessionViewModel.vehicleStats.collectAsState().value

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("$deviceName${if (isTestDevice) " (Mock)" else ""} — Statistics", fontSize = 20.sp) },
                navigationIcon = {
                    IconButton(onClick = onBackPressed) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = MaterialTheme.colorScheme.onSurface
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface,
                )
            )
        }
    ) { innerPadding ->
        when (state) {
            is SessionListState.Idle -> {
                Box(
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            "Load sessions to view statistics.",
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = onRefresh) { Text("Load Sessions") }
                    }
                }
            }

            is SessionListState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            "Requesting sessions...",
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                    }
                }
            }

            is SessionListState.Error -> {
                Box(
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Error: ${state.message}", color = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = onRefresh) { Text("Retry") }
                    }
                }
            }

            is SessionListState.Loaded -> {
                StatsContent(
                    sessions = state.sessions,
                    vehicleStats = vehicleStats,
                    onRefresh = onRefresh,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .background(MaterialTheme.colorScheme.background)
                )
            }
        }
    }
}

@Composable
private fun StatsContent(
    sessions: List<SessionInfo>,
    vehicleStats: OverallVehicleStats?,
    onRefresh: () -> Unit,
    modifier: Modifier = Modifier
) {
    if (sessions.isEmpty()) {
        Box(modifier = modifier, contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    "No sessions recorded yet.",
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Button(onClick = onRefresh) { Text("Refresh") }
            }
        }
        return
    }

    val completed    = sessions.filter { it.durationSeconds >= 0 }
    val ongoingCount = sessions.count { it.durationSeconds < 0 }
    val totalDuration = completed.sumOf { it.durationSeconds }
    val avgDuration  = if (completed.isNotEmpty()) totalDuration / completed.size else 0.0
    val maxDuration  = completed.maxOfOrNull { it.durationSeconds } ?: 0.0
    val firstSession = sessions.minByOrNull { it.startEpoch }
    val lastSession  = sessions.maxByOrNull { it.startEpoch }
    val dateFormat   = SimpleDateFormat("dd MMM yyyy", Locale.getDefault())

    LazyColumn(
        modifier = modifier.padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        contentPadding = PaddingValues(vertical = 16.dp)
    ) {
        // ── Header row ────────────────────────────────────────────────────────
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "${sessions.size} session${if (sessions.size != 1) "s" else ""}",
                    style = MaterialTheme.typography.titleMedium
                )
                TextButton(onClick = onRefresh) { Text("Refresh") }
            }
        }

        // ── Session summary cards ─────────────────────────────────────────────
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SummaryCard(Modifier.weight(1f), "Total Sessions", "${sessions.size}")
                SummaryCard(Modifier.weight(1f), "Ongoing", "$ongoingCount")
            }
        }
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SummaryCard(Modifier.weight(1f), "Total Time", formatDuration(totalDuration))
                SummaryCard(Modifier.weight(1f), "Avg Duration", formatDuration(avgDuration))
            }
        }
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SummaryCard(Modifier.weight(1f), "Longest", formatDuration(maxDuration))
                SummaryCard(Modifier.weight(1f), "Completed", "${completed.size}")
            }
        }

        // ── Date range card ────────────────────────────────────────────────────
        if (firstSession != null && lastSession != null) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(modifier = Modifier.padding(vertical = 4.dp)) {
                        InfoRow("First session", dateFormat.format(Date((firstSession.startEpoch * 1000).toLong())))
                        HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
                        InfoRow("Last session",  dateFormat.format(Date((lastSession.startEpoch  * 1000).toLong())))
                    }
                }
            }
        }

        // ── Engine analytics (only shown when vehicle_state data exists) ───────
        if (vehicleStats != null && vehicleStats.maxRpm > 0) {
            item {
                Text(
                    "Engine Analytics",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
            item {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SummaryCard(Modifier.weight(1f), "Avg RPM",  "${vehicleStats.avgRpm}")
                    SummaryCard(Modifier.weight(1f), "Max RPM",  "${vehicleStats.maxRpm}")
                }
            }
            item {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SummaryCard(Modifier.weight(1f), "Avg Coolant", "${"%.1f".format(vehicleStats.avgClt)} ºC")
                    SummaryCard(Modifier.weight(1f), "Max Speed",   "${"%.1f".format(vehicleStats.maxVss)} km/h")
                }
            }
        }

        // ── Session duration chart ─────────────────────────────────────────────
        if (completed.isNotEmpty()) {
            item {
                Text(
                    "Session Duration Overview",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
            items(completed.sortedByDescending { it.startEpoch }) { session ->
                SessionDurationBar(session = session, maxDuration = maxDuration)
            }
        }
    }
}

// ── Shared card composables ────────────────────────────────────────────────────

@Composable
private fun SummaryCard(modifier: Modifier = Modifier, label: String, value: String) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(value, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.height(4.dp))
            Text(label, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f))
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface)
    }
}

@Composable
private fun SessionDurationBar(session: SessionInfo, maxDuration: Double) {
    val dateFormat = SimpleDateFormat("dd MMM  HH:mm", Locale.getDefault())
    val startDate  = dateFormat.format(Date((session.startEpoch * 1000).toLong()))
    val fraction   = if (maxDuration > 0) (session.durationSeconds / maxDuration).toFloat().coerceIn(0f, 1f) else 0f
    val barColor   = MaterialTheme.colorScheme.primary
    val trackColor = MaterialTheme.colorScheme.surfaceVariant

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Session #${session.id}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface)
                Text(formatDuration(session.durationSeconds), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Text(startDate, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
            Spacer(modifier = Modifier.height(8.dp))
            Box(
                modifier = Modifier.fillMaxWidth().height(8.dp)
                    .background(trackColor, RoundedCornerShape(4.dp))
            ) {
                Box(
                    modifier = Modifier.fillMaxWidth(fraction).height(8.dp)
                        .background(barColor, RoundedCornerShape(4.dp))
                )
            }
        }
    }
}

private fun formatDuration(seconds: Double): String {
    if (seconds < 0) return "Ongoing"
    val total = seconds.toLong()
    val h = total / 3600
    val m = (total % 3600) / 60
    val s = total % 60
    return when {
        h > 0 -> "${h}h ${m}m ${s}s"
        m > 0 -> "${m}m ${s}s"
        else  -> "${s}s"
    }
}
