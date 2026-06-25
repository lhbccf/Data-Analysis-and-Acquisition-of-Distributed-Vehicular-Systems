import logging

from extra.session_manager import session_manager
from nextion.graph_renderer import build_graph_commands
from nextion.protocol import GraphRequest, NewSessionRequest
from repository import SessionRepo, StateRepo


logger = logging.getLogger(__name__)
DEFAULT_SESSION_DESCRIPTION = "CAN acquisition"


def send_cmd(ser, cmd):
    ser.write(cmd.encode())
    ser.write(b"\xff\xff\xff")

    if hasattr(ser, "flush"):
        ser.flush()


def send_graph_commands(ser, commands):
    for command in commands:
        send_cmd(ser, command)


def get_session_for_display_index(index, limit=5):
    sessions = SessionRepo.get_recent_sessions(limit)

    if index < 0 or index >= len(sessions):
        return None

    return sessions[index]


def build_graph_payload(request):
    session = get_session_for_display_index(request.session_index)
    if session is None:
        return None

    rows = StateRepo.get_vehicle_states_by_session_id(
        session_id=session.id,
        signals=request.signals,
    )

    return {
        "request": request,
        "session": session,
        "rows": rows,
    }


def handle_nextion_request(ser, request, config=None):
    if isinstance(request, NewSessionRequest):
        config = config or {}
        description = config.get(
            "session_description",
            DEFAULT_SESSION_DESCRIPTION,
        )
        return session_manager.start_new_session(description)

    if not isinstance(request, GraphRequest):
        logger.warning("Ignoring unsupported Nextion request: %r", request)
        return None

    payload = build_graph_payload(request)

    if payload is None:
        logger.warning(
            "Nextion graph request references missing session index %s",
            request.session_index,
        )
        return None

    logger.info(
        "Nextion graph request queued: session_index=%s session_id=%s "
        "signals=%s samples=%s",
        request.session_index,
        payload["session"].id,
        ",".join(request.signals),
        len(payload["rows"]),
    )

    commands = build_graph_commands(payload["rows"], request.signals, config)
    send_graph_commands(ser, commands)

    return payload
