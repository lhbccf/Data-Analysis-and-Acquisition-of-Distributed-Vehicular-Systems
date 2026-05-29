import logging

from nextion.protocol import GraphRequest
from repository import SessionRepo, StateRepo


logger = logging.getLogger(__name__)


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


def handle_graph_request(ser, request):
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

    # Next step: render payload["rows"] to an image and send it to the HMI.
    return payload
