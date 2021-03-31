import threading
import jsonpickle

from labo05.demo_networking.clientserver8.data.Som import Som


class ClientHandler(threading.Thread):

    numbers_clienthandlers = 0

    def __init__(self, socketclient, messages_queue):
        threading.Thread.__init__(self)
        # connectie with client
        self.socketclient = socketclient
        # message queue -> link to gui server
        self.messages_queue = messages_queue
        # id clienthandler
        self.id = ClientHandler.numbers_clienthandlers
        self.in_out_clh = self.socketclient.makefile(mode='rw')
        ClientHandler.numbers_clienthandlers += 1

    def run(self):

        self.print_bericht_gui_server("Waiting for numbers...")

        commando = self.in_out_clh.readline().rstrip('\n')
        while commando != "CLOSE":
            if commando == "SOM":

                json_data = self.in_out_clh.readline().rstrip('\n')
                s1 = jsonpickle.decode(json_data)

                s1.som = s1.getal1 + s1.getal2

                self.in_out_clh.write(jsonpickle.encode(s1) +"\n")
                self.in_out_clh.flush()
                self.print_bericht_gui_server(f"Sending sum {s1} back")

            commando = self.in_out_clh.readline().rstrip('\n')

        self.print_bericht_gui_server("Connection with client closed...")
        self.socketclient.close()

    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")
