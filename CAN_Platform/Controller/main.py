from UI.UI_Tests import RPMGaugeApp
from repository.database import database_manager
from controller import RequestController

import tkinter as tk


    
def command_request():
    x = input("Enter command (type 'help' for available commands): ")
    while x != "exit":
        match x:
            case "start_monitor": 
                root = tk.Tk()
                app = RPMGaugeApp(root)
                root.mainloop()
            case "start_session": 
                description = input("Enter session description: ")
                RequestController.create_session(description=description),
            case "create_can_frame": 
                session_id = int(input("Enter session ID: "))
                can_id = int(input("Enter CAN ID (hex): "), 16)
                dlc = int(input("Enter DLC: "))
                data = input("Enter data (hex): ")
                RequestController.create_can_frame(session_id=session_id, can_id=can_id, dlc=dlc, data=data),
            case "clear_session_frames": 
                session_id = int(input("Enter session ID: "))
                RequestController.clear_session_frames(session_id=session_id),
            case "end_session": 
                session_id = int(input("Enter session ID: "))
                RequestController.end_session(session_id=session_id),
            case "close_database": RequestController.close_database(),
            case "cleanup": database_manager.database_cleanup,
            case "teardown": database_manager.database_teardown
            case "help": 
                print("Available commands:" \
                "\n start_session," \
                "\n create_can_frame," \
                "\n clear_session_frames," \
                "\n end_session, cleanup," \
                "\n teardown," \
                "\n help," \
                "\n exit")
            case _: print("Unknown command")
        x = input("Enter command (type 'help' for available commands): ")
    

    

# Using the special variable 
# __name__
if __name__=="__main__":
    command_request()
