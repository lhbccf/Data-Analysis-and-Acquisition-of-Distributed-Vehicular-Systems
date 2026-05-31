package com.example.vehiculardataanalysis.screens.menu

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.example.vehiculardataanalysis.domain.SessionInfo
import com.example.vehiculardataanalysis.screens.viewmodel.SessionListState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SessionMenuScreen(
    deviceName: String = "Unknown Device",
    sessionViewModel: SessionViewModel,
    onBackPressed: () -> Unit,
    onRefresh: () -> Unit
) {
    val state = sessionViewModel.state.collectAsState().value

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("$deviceName — Sessions", fontSize = 20.sp) },
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.background)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            when (state) {
                is SessionListState.Idle -> {
                    Spacer(modifier = Modifier.weight(1f))
                    Text(
                        "No sessions loaded.",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = onRefresh) { Text("Load Sessions") }
                    Spacer(modifier = Modifier.weight(1f))
                }

                is SessionListState.Loading -> {
                    Spacer(modifier = Modifier.weight(1f))
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        "Requesting sessions...",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.weight(1f))
                }

                is SessionListState.Error -> {
                    Spacer(modifier = Modifier.weight(1f))
                    Text("Error: ${state.message}", color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = onRefresh) { Text("Retry") }
                    Spacer(modifier = Modifier.weight(1f))
                }

                is SessionListState.Loaded -> {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            "${state.sessions.size} session${if (state.sessions.size != 1) "s" else ""}",
                            style = MaterialTheme.typography.titleMedium
                        )
                        TextButton(onClick = onRefresh) { Text("Refresh") }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    if (state.sessions.isEmpty()) {
                        Spacer(modifier = Modifier.weight(1f))
                        Text(
                            "No sessions recorded yet.",
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                        Spacer(modifier = Modifier.weight(1f))
                    } else {
                        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            items(state.sessions) { session -> SessionCard(session) }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SessionCard(session: SessionInfo) {
    val dateFormat = SimpleDateFormat("dd MMM yyyy  HH:mm:ss", Locale.getDefault())
    val startDate = dateFormat.format(Date((session.startEpoch * 1000).toLong()))
    val duration = if (session.durationSeconds < 0) {
        "Ongoing"
    } else {
        val total = session.durationSeconds.toLong()
        val h = total / 3600
        val m = (total % 3600) / 60
        val s = total % 60
        when {
            h > 0  -> "${h}h ${m}m ${s}s"
            m > 0  -> "${m}m ${s}s"
            else   -> "${s}s"
        }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "Session #${session.id}",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    duration,
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (session.durationSeconds < 0)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                startDate,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
        }
    }
}
