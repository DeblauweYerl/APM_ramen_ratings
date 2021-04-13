import threading
import jsonpickle
import json

from APM_ramen_ratings.data.RatingRepository import RatingRepository
from APM_ramen_ratings.data.AccountRepository import AccountRepository


class ClientHandler(threading.Thread):

    _repository = None

    def __init__(self, socketclient, messages_queue, server_window):
        threading.Thread.__init__(self)
        # connectie with client
        self.socketclient = socketclient
        # message queue -> link to gui server
        self.messages_queue = messages_queue
        # id clienthandler
        self.id = f'CL_{threading.get_ident()}'
        self.in_out_clh = self.socketclient.makefile(mode='rw')
        self.rating_repository = RatingRepository()
        self.account_repository = AccountRepository()
        self.server_window = server_window

    def run(self):
        command = json.loads(self.in_out_clh.readline().rstrip('\n'))
        while command['command'] != "disconnect":
            if command['command'] == "data":
                if command['params']['data'] == "all":
                    filters = command['params']['filters']
                    msg_out = self.rating_repository.get_filtered_ratings(filters)
                    self.print_message_gui_server(f"sending data with filters: {filters}")

                elif command['params']['data'] == "brand":
                    msg_out = self.rating_repository.get_brands()
                    self.print_message_gui_server(f"sending all brands")

                elif command['params']['data'] == "country":
                    msg_out = self.rating_repository.get_countries()
                    self.print_message_gui_server(f"sending all countries")

                elif command['params']['data'] == "brand_stats":
                    msg_out = self.rating_repository.get_mean_brand_rating()
                    self.print_message_gui_server(f"sending all brand statistics")

                elif command['params']['data'] == "search":
                    search = command['params']['search']
                    msg_out = self.rating_repository.search_ratings(search)
                    self.print_message_gui_server(f"sending data from search action: '{search}'")

                msg_out = jsonpickle.encode(msg_out)
                self.in_out_clh.write(msg_out + "\n")
                self.in_out_clh.flush()

            elif command['command'] == "log_in":
                self.email = command['params']['email']
                self.server_window.cl_lstclients.insert('end', command['params']['email'])
                self.print_message_gui_server(f"account logged in: {command['params']}")
                self.print_message_gui_server(self.account_repository.add_account(command['params']))

            command = json.loads(self.in_out_clh.readline().rstrip('\n'))

        self.server_window.remove_client(self.email)
        self.print_message_gui_server(f"disconnected {self.id}")
        self.socketclient.close()

    def print_message_gui_server(self, message):
        try:
            self.messages_queue.put(f"CLH {self.email}:> {message}")
        except AttributeError as ae:
            print(ae)
