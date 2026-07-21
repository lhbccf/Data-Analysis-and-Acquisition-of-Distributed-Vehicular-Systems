package com.example.vehiculardataanalysis.screens.menu

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.vehiculardataanalysis.domain.SessionInfo
import com.example.vehiculardataanalysis.screens.viewmodel.AsyncState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionListState
import com.example.vehiculardataanalysis.screens.viewmodel.SessionViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SessionMenuScreen(
    deviceName: String = "Unknown Device",
    isTestDevice: Boolean = false,
    sessionViewModel: SessionViewModel,
    onBackPressed: () -> Unit,
    onRefresh: () -> Unit,
    onSessionSelected: (SessionInfo) -> Unit = {},
    onCreateSession: () -> Unit = {},
    onEndSession: () -> Unit = {}
) {
    val uiState     = sessionViewModel.uiState.collectAsState().value
    val state       = uiState.sessionList
    val actionState = uiState.actionState

    // ── Dialog state ─────────────────────────────────────────────────────────
    var showCreateDialog by remember { mutableStateOf(false) }
    var showEndDialog    by remember { mutableStateOf(false) }

    val ongoingSession = (state as? SessionListState.Loaded)
        ?.sessions?.firstOrNull { it.durationSeconds < 0 }

    // ── Error dialog from action failures ────────────────────────────────────
    if (actionState is AsyncState.Error) {
        AlertDialog(
            onDismissRequest = { sessionViewModel.clearActionError() },
            title = { Text("Action Failed") },
            text  = { Text(actionState.message) },
            confirmButton = {
                TextButton(onClick = { sessionViewModel.clearActionError() }) { Text("OK") }
            },
            containerColor = MaterialTheme.colorScheme.surfaceVariant,
            titleContentColor = MaterialTheme.colorScheme.onSurface,
            textContentColor  = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }

    // ── Create session confirmation ───────────────────────────────────────────
    if (showCreateDialog) {
        val title: String
        val body: String
        val confirmLabel: String
        if (ongoingSession != null) {
            title        = "Active Session Running"
            body         = "Session #${ongoingSession.id} is currently recording. " +
                           "A new session cannot start until it ends.\n\n" +
                           "End session #${ongoingSession.id} and start a new one?"
            confirmLabel = "End & Create"
        } else {
            title        = "Start New Session"
            body         = "Begin a new recording session?"
            confirmLabel = "Start"
        }
        AlertDialog(
            onDismissRequest = { showCreateDialog = false },
            title = { Text(title) },
            text  = { Text(body) },
            dismissButton = {
                TextButton(onClick = { showCreateDialog = false }) { Text("Cancel") }
            },
            confirmButton = {
                Button(onClick = {
                    showCreateDialog = false
                    onCreateSession()
                }) { Text(confirmLabel) }
            },
            containerColor = MaterialTheme.colorScheme.surfaceVariant,
            titleContentColor = MaterialTheme.colorScheme.onSurface,
            textContentColor  = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }

    // ── End session confirmation ──────────────────────────────────────────────
    if (showEndDialog && ongoingSession != null) {
        AlertDialog(
            onDismissRequest = { showEndDialog = false },
            title = { Text("End Recording Session") },
            text  = { Text("Stop recording for session #${ongoingSession.id}?") },
            dismissButton = {
                TextButton(onClick = { showEndDialog = false }) { Text("Cancel") }
            },
            confirmButton = {
                Button(
                    onClick = {
                        showEndDialog = false
                        onEndSession()
                    }
                ) { Text("End Session") }
            },
            containerColor = MaterialTheme.colorScheme.surfaceVariant,
            titleContentColor = MaterialTheme.colorScheme.onSurface,
            textContentColor  = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("$deviceName${if (isTestDevice) " (Mock)" else ""} — Sessions", fontSize = 20.sp) },
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
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.background)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = { showCreateDialog = true },
                    modifier = Modifier.weight(1f),
                    enabled = actionState !is AsyncState.Loading
                ) {
                    if (actionState is AsyncState.Loading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(18.dp),
                            strokeWidth = 2.dp,
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text("New Session")
                    }
                }
                Button(
                    onClick = { showEndDialog = true },
                    modifier = Modifier.weight(1f),
                    enabled = ongoingSession != null && actionState !is AsyncState.Loading,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error,
                        contentColor = MaterialTheme.colorScheme.onError,
                        disabledContainerColor = MaterialTheme.colorScheme.error.copy(alpha = 0.38f),
                        disabledContentColor = MaterialTheme.colorScheme.onError.copy(alpha = 0.38f)
                    )
                ) {
                    Text("End Session")
                }
            }

            when (state) {
                is AsyncState.Idle -> {
                    Spacer(modifier = Modifier.weight(1f))
                    Text(
                        "No sessions loaded.",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = onRefresh) { Text("Load Sessions") }
                    Spacer(modifier = Modifier.weight(1f))
                }

                is AsyncState.Loading -> {
                    Spacer(modifier = Modifier.weight(1f))
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        "Requesting sessions...",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                    Spacer(modifier = Modifier.weight(1f))
                }

                is AsyncState.Error -> {
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
                        LazyColumn(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            items(state.sessions) { session ->
                                SessionCard(session, onClick = { onSessionSelected(session) })
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SessionCard(session: SessionInfo, onClick: () -> Unit) {
    val dateFormat = SimpleDateFormat("dd MMM yyyy  HH:mm:ss", Locale.getDefault())
    val startDate = dateFormat.format(Date((session.startEpoch * 1000).toLong()))
    val isOngoing = session.durationSeconds < 0
    val duration = if (isOngoing) {
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
        onClick = onClick,
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
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        "Session #${session.id}",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        startDate,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        duration,
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (isOngoing)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                        contentDescription = "View stats",
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
                    )
                }
            }
        }
    }
}
