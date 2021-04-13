import logging
import socket
from queue import Queue
from threading import Thread
import numpy as np

from tkinter import *

from APM_ramen_ratings.server.server import RamenServer
from APM_ramen_ratings.data.AccountRepository import AccountRepository


class ServerWindow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.server = None
        self.thread_listener_queue=None
        self.init_messages_queue()
        self.account_repository = AccountRepository()


    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Server")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(2, weight=5)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(3, weight=1)

        Label(self, text="Connected clients:").grid(row=0, column=0, columnspan=2)
        cl_scrollbar = Scrollbar(self, orient=VERTICAL)
        self.cl_lstclients = Listbox(self, yscrollcommand=cl_scrollbar.set)
        self.cl_lstclients.grid(row=1, column=0, sticky=N+S+E+W)
        self.cl_lstclients.bind('<Double-1>', self.details_client)
        cl_scrollbar.config(command=self.cl_lstclients.yview)
        cl_scrollbar.grid(row=1, column=1, sticky=N+S+W)

        Label(self, text="Function popularity:").grid(row=2, column=0)
        self.pop_scrollbar = Scrollbar(self, orient=VERTICAL)
        self.pop_lstfunctions = Listbox(self, yscrollcommand=self.pop_scrollbar.set)
        self.pop_scrollbar.config(command=self.pop_lstfunctions.yview)
        self.pop_lstfunctions.grid(row=3, column=0, sticky=N + S + E + W)

        Label(self, text="Server log:").grid(row=0, column=2)
        self.log_scrollbar = Scrollbar(self, orient=VERTICAL)
        self.log_lstnumbers = Listbox(self, yscrollcommand=self.log_scrollbar.set)
        self.log_scrollbar.config(command=self.log_lstnumbers.yview)
        self.log_lstnumbers.grid(row=1, column=2, rowspan=3, sticky=N + S + E + W)
        self.log_scrollbar.grid(row=1, column=3, rowspan=3, sticky=N + S)

        self.btn_text = StringVar()
        self.btn_text.set("Start server")
        self.buttonServer = Button(self, textvariable=self.btn_text, command=self.start_stop_server)
        self.buttonServer.grid(row=4, column=0, columnspan=4, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

    ### UI interaction ###
    def details_client(self, eventargs):
        self.account_repository.update_accounts()
        account = np.ndarray.flatten(self.account_repository.get_account(self.cl_lstclients.get(ACTIVE)))
        window = Tk()
        self.init_window_client_details(window, account)
        window.mainloop()

    def init_window_client_details(self, root, account):
        root.title("client details")

        Label(root, text='nickname:').grid(padx=5, pady=5, sticky=W)
        Label(root, text=account[0]).grid(row=0, column=1, padx=5, pady=5, sticky=W)

        Label(root, text='name:').grid(padx=5, pady=5, sticky=W)
        Label(root, text=account[1]).grid(row=1, column=1, padx=5, pady=5, sticky=W)

        Label(root, text='email:').grid(padx=5, pady=5, sticky=W)
        Label(root, text=account[2]).grid(row=2, column=1, padx=5, pady=5, sticky=W)

        Label(root, text='message to client:').grid(padx=5, pady=(20,5), sticky=W)
        Entry(root, width=50).grid(columnspan=2, padx=5, pady=5, sticky=E+W)
        Button(root, text='send message').grid(padx=5, pady=5, sticky=W)

    def client_send_message(self):
        pass

    def remove_client(self, email):
        index = self.cl_lstclients.get().index(email)
        self.cl_lstclients.delete(index, index)

    ### server activity ###
    def start_stop_server(self):
        if self.server is not None:
            self.__stop_server()
        else:
            self.__start_server()

    def __start_server(self):
        self.server = RamenServer(socket.gethostname(), 9999, self.messages_queue, self)
        self.server.init_server()
        self.server.start()  # in thread plaatsen!
        logging.info("Server started")
        self.btn_text.set("Stop server")

    def __stop_server(self):
        self.server.stop_server()
        self.server = None
        logging.info("Server stopped")
        self.btn_text.set("Start server")

    ### client connection ###
    def connect_client(self, client_id):
        self.cl_lstclients.insert(END, client_id)

    def disconnect_client(self, client_id):
        print(self.cl_lstclients.get(0, END))

    ### message queue ###
    def init_messages_queue(self):
        self.messages_queue = Queue()
        self.thread_listener_queue = Thread(target=self.print_messsages_from_queue, name="Queue_listener_thread", daemon=True)
        self.thread_listener_queue.start()

    def print_messsages_from_queue(self):
        message = self.messages_queue.get().split(' ')
        while message[0] != "stop":
            # if message[1] == '/connect':
            #     self.connect_client(message[2])
            # elif message[1] == '/disconnect':
            #     self.disconnect_client(message[2])
            self.log_lstnumbers.insert(END, message)
            self.log_lstnumbers.yview(END)
            self.messages_queue.task_done()
            message = self.messages_queue.get().split(' ')
