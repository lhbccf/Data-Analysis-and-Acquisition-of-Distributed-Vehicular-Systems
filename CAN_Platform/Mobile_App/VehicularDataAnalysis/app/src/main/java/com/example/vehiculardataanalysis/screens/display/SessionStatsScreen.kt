package com.example.vehiculardataanalysis.screens.display

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.screens.viewmodel.AsyncState
import com.example.vehiculardataanalysis.screens.viewmodel.OverallVehicleStats
import com.example.vehiculardataanalysis.screens.viewmodel.SessionStatsState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SessionStatsScreen(
    sessionId: Int,
    sessionStartEpoch: Double,
    sessionDurationSeconds: Double,
    deviceName: String = "Unknown Device",
    isTestDevice: Boolean = false,
    sessionViewModel: SessionViewModel,
    onBackPressed: () -> Unit,
    onRetry: () -> Unit
) {
    val statsState = sessionViewModel.uiState.collectAsState().value.sessionStats

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(
                        "$deviceName${if (isTestDevice) " (Mock)" else ""} — Session #$sessionId",
                        fontSize = 20.sp
                    )
                },
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
        when (statsState) {
            is AsyncState.Idle -> {
                Box(
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            "No statistics loaded.",
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = onRetry) { Text("Load Stats") }
                    }
                }
            }

            is AsyncState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            "Requesting session statistics...",
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                    }
                }
            }

            is AsyncState.Error -> {
                Box(
                    modifier = Modifier.fillMaxSize().padding(innerPadding),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Error: ${statsState.message}", color = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = onRetry) { Text("Retry") }
                    }
                }
            }

            is SessionStatsState.Loaded -> {
                SessionStatsContent(
                    sessionId = sessionId,
                    sessionStartEpoch = sessionStartEpoch,
                    sessionDurationSeconds = sessionDurationSeconds,
                    stats = statsState.stats,
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
private fun SessionStatsContent(
    sessionId: Int,
    sessionStartEpoch: Double,
    sessionDurationSeconds: Double,
    stats: OverallVehicleStats,
    modifier: Modifier = Modifier
) {
    val dateFormat = SimpleDateFormat("dd MMM yyyy  HH:mm:ss", Locale.getDefault())
    val startDate = dateFormat.format(Date((sessionStartEpoch * 1000).toLong()))
    val duration = formatDuration(sessionDurationSeconds)

    LazyColumn(
        modifier = modifier.padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        contentPadding = PaddingValues(vertical = 16.dp)
    ) {
        //Session info card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(vertical = 4.dp)) {
                    SessionInfoRow("Session", "#$sessionId")
                    HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
                    SessionInfoRow("Started", startDate)
                    HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
                    SessionInfoRow("Duration", duration)
                }
            }
        }

        //Engine analytics
        if (stats.maxRpm > 0) {
            item {
                Text(
                    "Engine Analytics",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
            item {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SessionSummaryCard(Modifier.weight(1f), "Avg RPM",  "${stats.avgRpm}")
                    SessionSummaryCard(Modifier.weight(1f), "Max RPM",  "${stats.maxRpm}")
                }
            }
            item {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SessionSummaryCard(Modifier.weight(1f), "Avg Coolant", "${"%.1f".format(stats.avgClt)} ºC")
                    SessionSummaryCard(Modifier.weight(1f), "Max Speed",   "${"%.1f".format(stats.maxVss)} km/h")
                }
            }
        } else {
            item {
                Box(
                    modifier = Modifier.fillMaxWidth().padding(top = 32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "No engine data recorded for this session.",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

@Composable
private fun SessionSummaryCard(modifier: Modifier = Modifier, label: String, value: String) {
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
private fun SessionInfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface)
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
