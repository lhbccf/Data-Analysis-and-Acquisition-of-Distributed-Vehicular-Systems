from repository import SessionRepo, CANFrameRepo, SignalRepo, StateRepo

def close_database():
    SessionRepo.conn.close()
    CANFrameRepo.conn.close()
    SignalRepo.conn.close()
	StateRepo.conn.close()
	
def create_session(description: str):
    return SessionRepo.create_session(description=description)

def create_can_frame(session_id: int, can_id: int, dlc: int, data: str):
    return CANFrameRepo.create_can_frame(session_id=session_id, can_id=can_id, dlc=dlc, data=data)

def create_signal(can_frame_id: int, signal_name: str, signal_value: str, signal_unit: str):
    return SignalRepo.create_signal(can_frame_id=can_frame_id, signal_name=signal_name, signal_value=signal_value, signal_unit=signal_unit)

def end_session(session_id: int):
    SessionRepo.end_session(session_id=session_id)

def clear_session_frames(session_id: int):
    SessionRepo.clear_session_frames(session_id=session_id)

def create_vehicle_state(state: dict):

	return VehicleStateRepo.create_vehicle_state(
		state=state
	)

def get_latest_vehicle_state():

    return VehicleStateRepo.get_latest_vehicle_state()


def get_all_vehicle_states():

    return VehicleStateRepo.get_all_vehicle_states()


def delete_all_vehicle_states():

    VehicleStateRepo.delete_all_vehicle_states()
