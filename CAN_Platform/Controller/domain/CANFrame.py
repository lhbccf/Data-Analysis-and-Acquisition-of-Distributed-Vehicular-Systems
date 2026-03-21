class CANFrame:

    def __init__(self, can_frame_id, session_id, timestamp, can_id, dlc, data):
        self.can_frame_id = can_frame_id
        self.session_id = session_id
        self.timestamp = timestamp
        self.can_id = can_id
        self.dlc = dlc
        self.data = data

