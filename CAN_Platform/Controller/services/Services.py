from repository import CANFrameRepo, SessionRepo, SignalRepo, StateRepo


def close_database():
    SessionRepo.close_database()
    CANFrameRepo.close_database()
    SignalRepo.close_database()
    StateRepo.close_database()


def create_session(description: str):
    return SessionRepo.create_session(description=description)


def create_can_frame(
    session_id: int,
    can_id: int,
    dlc: int,
    data: str,
    timestamp=None,
):
    return CANFrameRepo.create_can_frame(
        session_id=session_id,
        can_id=can_id,
        dlc=dlc,
        data=data,
        timestamp=timestamp,
    )


def create_signal(
    can_frame_id: int,
    signal_name: str,
    signal_value: str,
    signal_unit: str,
):
    return SignalRepo.create_signal(
        can_frame_id=can_frame_id,
        signal_name=signal_name,
        signal_value=signal_value,
        signal_unit=signal_unit,
    )


def show_signals_by_can_frame(can_frame_id: int):
    return SignalRepo.get_signals_by_can_frame_id(can_frame_id=can_frame_id)

def show_signals_by_session(session_id: int):
    return SignalRepo.get_signals_by_session_id(session_id=session_id)

def end_session(session_id: int):
    SessionRepo.end_session(session_id=session_id)


def clear_session_frames(session_id: int):
    SessionRepo.clear_session_frames(session_id=session_id)


def create_vehicle_state(state: dict):
    return StateRepo.create_vehicle_state(state=state)


def get_latest_vehicle_state():
    return StateRepo.get_latest_vehicle_state()


def get_all_vehicle_states():
    return StateRepo.get_all_vehicle_states()


def delete_all_vehicle_states():
    StateRepo.delete_all_vehicle_states()


def get_recent_sessions(limit=5):
    return SessionRepo.get_recent_sessions(limit)


def get_vehicle_states_by_session_id(session_id, signals):
    return StateRepo.get_vehicle_states_by_session_id(session_id, signals)
