import logging
import threading
from tkinter import *

from APM_ramen_ratings.server.gui_server import ServerWindow

logging.basicConfig(level=logging.DEBUG)

def client_disconnected():
    # even controleren overlopen van actieve threads wanneer window gesloten wordt
    logging.debug("Active threads:")
    for thread in threading.enumerate():
        logging.debug(f">Thread name is {thread.getName()}.")
    root.destroy()

root = Tk()
root.geometry("1000x500")
gui_server = ServerWindow(root)
root.protocol("WM_DELETE_WINDOW", client_disconnected)
root.mainloop()
