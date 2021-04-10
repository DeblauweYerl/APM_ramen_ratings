from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import logging
import socket
import jsonpickle
import json


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.server_connect()

    def init_window(self):
        self.master.title("Ramen ratings")
        self.pack(fill=BOTH, expand=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        # configure tabs
        # tab_control = ttk.Notebook(self)
        #
        # tab1 = ttk.Frame(tab_control)
        #
        # tab_control.pack(fill=BOTH, expand=1)
        # tab1.pack(fill=BOTH, expand=1)
        #
        # tab_control.add(tab1, text="all ratings")

        # tab1: all ratings

        # filters
        self.tab1_select_brand = ttk.Combobox(self, height=25, state='readonly')
        self.tab1_select_brand.grid(column=0, row=0, padx=(2, 10), pady=5, sticky=N+S+E+W)

        self.tab1_select_country = ttk.Combobox(self, height=25, state='readonly')
        self.tab1_select_country.grid(column=1, row=0, padx=(2, 10), pady=5, sticky=N+S+E+W)

        ttk.Label(self, text="min. rating:").grid(column=2, row=0, pady=5, sticky=N+S+E+W)
        self.tab1_min_rating = Scale(self, from_=0, to=5, tickinterval=5, orient=HORIZONTAL, length=150)
        self.tab1_min_rating.grid(column=3, row=0, padx=(10, 2), pady=5, sticky=N+S+E+W)

        tab1_btn_apply_filters = Button(self, text="Apply filters", command=self.tab1_apply_filters)
        tab1_btn_apply_filters.grid(column=0, row=1, padx=(2, 10), pady=5, sticky=N+S+E+W)

        # data
        columns_ratings = ('brand', 'country', 'variety', 'rating')
        self.tab1_ratings = ttk.Treeview(self, columns=columns_ratings, show='headings')
        self.tab1_ratings.grid(padx=(2, 0))
        tab1_ratings_scrollbar = Scrollbar(self, orient=VERTICAL)
        self.tab1_ratings.configure(yscrollcommand=tab1_ratings_scrollbar.set)
        tab1_ratings_scrollbar.config(command=self.tab1_ratings.yview)
        tab1_ratings_scrollbar.grid(row=3, column=4, padx=(0, 2), sticky=N + S + E + W)

        # for col in columns_ratings:
        #     self.tab1_ratings.heading(col, text=col, command=lambda: self.tab1_table_sort(self.tab1_ratings, col, False))

        self.tab1_ratings.heading('#1', text='brand')
        self.tab1_ratings.heading('#2', text='country')
        self.tab1_ratings.heading('#3', text='variety')
        self.tab1_ratings.heading('#4', text='rating')

        self.tab1_ratings.column('#1', width=150, stretch=YES)
        self.tab1_ratings.column('#2', width=120, stretch=YES)
        self.tab1_ratings.column('#3', width=450, stretch=YES)
        self.tab1_ratings.column('#4', width=60, stretch=YES)

        self.tab1_ratings.grid(row=3, columnspan=4, sticky=N + S + E + W)

    ### server ###
    def server_connect(self):
        try:
            logging.info("Making connection with server...")
            # get local machine name
            host = socket.gethostname()
            port = 9999
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            self.s.connect((host, port))
            self.in_out_server = self.s.makefile(mode='rw')
            logging.info("Connection with server successful.")

            # initialize tabs
            self.init_tab1()

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("RamenRatings - error", "Cannot connect to server.")

    def server_disconnect(self):
        try:
            logging.info("Close connection with server...")
            self.in_out_server.write("CLOSE\n")
            self.in_out_server.flush()
            self.s.close()
        except Exception as ex:
            logging.error("Foutmelding:close connection with server failed")

    ### general ###
    def load_filter(self, filter_name, obj):
        command = {'command': 'data',
                   'params': {
                       'data': filter_name
                   }}
        self.in_out_server.write(json.dumps(command) + "\n")
        self.in_out_server.flush()
        filter_values = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
        filter_values.insert(0, filter_name)
        obj['values'] = filter_values
        obj.set(filter_name)

    def load_treeview_ratings(self, data, treeview_obj):
        [treeview_obj.delete(record) for record in treeview_obj.get_children()]
        [treeview_obj.insert('', index='end', values=(rt[1], rt[4], rt[2], rt[5])) for rt in data]

    ### tab1 ###
    def init_tab1(self):
        self.load_filter('brand', self.tab1_select_brand)
        self.load_filter('country', self.tab1_select_country)
        self.tab1_apply_filters()

    def tab1_apply_filters(self):
        command = {'command': 'data',
                   'params': {
                       'data': 'all',
                       'filters': {
                           'brand': self.tab1_select_brand.get(),
                           'country': self.tab1_select_country.get(),
                           'min_rating': self.tab1_min_rating.get()
                       }
                   }}
        try:
            self.in_out_server.write(json.dumps(command) + "\n")
            self.in_out_server.flush()
            ratings = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
            self.load_treeview_ratings(ratings, self.tab1_ratings)
        except Exception as ex:
            print(ex)

    # def tab1_table_sort(self, tv, col, reverse):
    #     ls = [(tv.set(k, col), k) for k in tv.get_children('')]
    #     ls.sort(reverse=reverse)
    #
    #     # rearrange items in sorted positions
    #     for index, (val, k) in enumerate(ls):
    #         tv.move(k, '', index)
    #
    #     # reverse sort next time
    #     tv.heading(col, command=lambda: self.tab1_table_sort(tv, col, not reverse))



root = Tk()
app = Window(root)
root.mainloop()
