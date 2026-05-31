from dataclasses import dataclass


@dataclass(frozen=True)
class GraphRequest:
    session_index: int
    signals: tuple


@dataclass(frozen=True)
class NewSessionRequest:
    pass


SIGNAL_ALIASES = {
    "adv": "advance",
    "pw": "pulse_width",
}

NEW_SESSION_COMMAND = "NEW_SESSION"
PARAMS_PREFIX = "PARAMS:"


def normalize_signal_name(name):
    name = name.strip().lower()
    return SIGNAL_ALIASES.get(name, name)


def parse_nextion_message(message):
    if isinstance(message, bytes):
        message = message.replace(b"\xff", b"").decode(errors="ignore")

    message = message.strip().strip("|").strip()

    if message == NEW_SESSION_COMMAND:
        return NewSessionRequest()

    if not message.startswith(PARAMS_PREFIX):
        return None

    parts = message.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid PARAMS message: {message!r}")

    try:
        session_index = int(parts[1])
    except ValueError as exc:
        raise ValueError(f"Invalid session index: {parts[1]!r}") from exc

    signals = tuple(
        normalize_signal_name(signal)
        for signal in parts[2].split(",")
        if signal.strip()
    )

    if not signals:
        raise ValueError("PARAMS message does not include any signals")

    return GraphRequest(session_index=session_index, signals=signals)
