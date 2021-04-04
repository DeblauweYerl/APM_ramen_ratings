import threading
import jsonpickle
import json

from APM_ramen_ratings.data import RatingRepository


class ClientHandler(threading.Thread):

    _repository = None

    def __init__(self, socketclient, messages_queue, repository, server_window):
        threading.Thread.__init__(self)
        # connectie with client
        self.socketclient = socketclient
        # message queue -> link to gui server
        self.messages_queue = messages_queue
        # id clienthandler
        self.id = f'CL_{threading.get_ident()}'
        self.in_out_clh = self.socketclient.makefile(mode='rw')
        self.repository = repository
        self.server_window = server_window
        self.server_window.cl_lstclients.insert('end', self.id)

    def run(self):

        self.print_bericht_gui_server("Waiting for numbers...")
        command = json.loads(jsonpickle.decode(self.in_out_clh.readline().rstrip('\n')))
        print(command)
        while command['command'] != "stop":
            if command['command'] == "data":
                if command['params']['data'] == "all":
                    filters = command['params']['filters']
                    ratings = self.repository.get_filtered_ratings(filters)
                    self.in_out_clh.write(jsonpickle.encode(ratings) +"\n")
                    self.in_out_clh.flush()
                    self.print_bericht_gui_server(f"sending data with filters: {filters}")

                elif command['params']['data'] == "brands":
                    brands = self.repository.get_brands()
                    self.in_out_clh.write(jsonpickle.encode(brands) +"\n")
                    self.in_out_clh.flush()
                    self.print_bericht_gui_server(f"sending all brands")

                elif command['params']['data'] == "countries":
                    countries = self.repository.get_countries()
                    self.in_out_clh.write(jsonpickle.encode(countries) +"\n")
                    self.in_out_clh.flush()
                    self.print_bericht_gui_server(f"sending all countries")

            command = self.in_out_clh.readline().rstrip('\n')
            if command != '':
                command = json.loads(jsonpickle.decode(self.in_out_clh.readline().rstrip('\n')))
            else:
                command = {'command': 'stop'}
                print(self.server_window.cl_lstclients.get(first=0))

        self.print_bericht_gui_server(f"/disconnect {self.id}")

        self.socketclient.close()

    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")
