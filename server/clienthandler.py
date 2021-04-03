import threading
import jsonpickle

from APM_ramen_ratings.data import RatingRepository


class ClientHandler(threading.Thread):

    numbers_clienthandlers = 0

    def __init__(self, socketclient, messages_queue):
        threading.Thread.__init__(self)
        # connectie with client
        self.socketclient = socketclient
        # message queue -> link to gui server
        self.messages_queue = messages_queue
        # id clienthandler
        self.id = f'CL_{threading.get_ident()}'
        self.in_out_clh = self.socketclient.makefile(mode='rw')
        # data
        self.repository = RatingRepository()

    def run(self):

        self.print_bericht_gui_server("Waiting for numbers...")

        command = self.in_out_clh.readline().rstrip('\n').split(" ")
        while command[0] != "/stop":
            if command[0] == "/data":
                if command[1] == "all":
                    filters = jsonpickle.decode(command[2])
                    ratings = self.repository.get_filtered_ratings(filters)
                    self.in_out_clh.write(jsonpickle.encode(ratings) +"\n")
                    self.in_out_clh.flush()
                    self.print_bericht_gui_server(f"sending data with filters: {filters}")

                elif command[1] == "brands":
                    brands = self.repository.get_brands()
                    self.in_out_clh.write(jsonpickle.encode(brands) +"\n")
                    self.in_out_clh.flush()
                    self.print_bericht_gui_server(f"returning all brands")

                elif command[1] == "countries":
                    countries = self.repository.get_countries()
                    self.in_out_clh.write(jsonpickle.encode(countries) +"\n")
                    self.in_out_clh.flush()
                    self.print_bericht_gui_server(f"returning all countries")

            command = self.in_out_clh.readline().rstrip('\n')

        self.print_bericht_gui_server(f"/disconnect {self.id}")
        self.socketclient.close()

    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")
