class CANFrame:

    def __init__(self, id, session_id, timestamp, can_id, dlc, data):
        self.id = id
        self.session_id = session_id
        self.timestamp = timestamp
        self.can_id = can_id
        self.dlc = dlc
        self.data = data

