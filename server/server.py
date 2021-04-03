import logging
import socket
import threading

from APM_ramen_ratings.server.clienthandler import ClientHandler
from APM_ramen_ratings.data.RatingRepository import RatingRepository

class RamenServer(threading.Thread):
    def __init__(self, host, port, messages_queue):
        threading.Thread.__init__(self, name="Thread-Server", daemon=True)
        self.serversocket = None
        self.__is_connected = False
        self.host = host
        self.port = port
        self.messages_queue = messages_queue
        self.repository = RatingRepository()

    @property
    def is_connected(self):
        return self.__is_connected

    def init_server(self):
        # create a socket object
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.__is_connected = True
        self.print_bericht_gui_server("SERVER STARTED")

    def stop_server(self):
        if self.serversocket is not None:
            self.serversocket.close()
            self.serversocket = None
            self.__is_connected = False
            logging.info("Serversocket closed")

    # thread-klasse!
    def run(self):
        number_received_message = 0
        try:
            while True:
                logging.debug("server waiting for a new client")
                self.print_bericht_gui_server("waiting for a new client...")

                # establish a connection
                socket_to_client, addr = self.serversocket.accept()
                self.print_bericht_gui_server(f"received connection from {addr}")
                clh = ClientHandler(socket_to_client, self.messages_queue, self.repository)
                clh.start()
                self.print_bericht_gui_server(f"current thread count: {threading.active_count()}.")

        except Exception as ex:
            self.print_bericht_gui_server("serversocket closed")
            logging.debug("Thread server ended")


    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"Server:> {message}")
