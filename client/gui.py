from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import logging
import socket
import jsonpickle
import json

from APM_ramen_ratings.data.RatingRepository import RatingRepository


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.ratings = RatingRepository()
        self.init_window()
        self.server_connect()

    def init_window(self):
        self.master.title("Ramen ratings")

        # self.pack(fill=BOTH, expand=1)
        self.grid(sticky=N+S+E+W)


        # configure tabs
        tab_control = ttk.Notebook(self.master)

        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)

        # tab_control.pack(fill=BOTH, expand=1)
        tab_control.grid(sticky=N+S+E+W)
        # tab1.pack(fill=BOTH, expand=1)
        # tab1.grid(sticky=N+S+E+W)
        self.tab1 = tab1

        tab_control.add(tab1, text="all ratings")
        tab_control.add(tab2, text="brand popularity")



        # tab1: all ratings
        # filters
        # Label(tab1, text="filters").grid(column=0, row=0, padx=10, pady=2)

        self.tab1_select_brand = ttk.Combobox(tab1)
        self.tab1_select_brand.grid(column=0, row=0, padx=5, pady=2, sticky=W)

        self.tab1_select_country = ttk.Combobox(tab1)
        self.tab1_select_country.grid(column=1, row=0, padx=15, pady=2, sticky=W)

        ttk.Label(tab1, text="min. rating:").grid(column=2, row=0, padx=5, pady=2, sticky=W)
        self.tab1_min_rating = Scale(tab1, from_=0, to=5, tickinterval=5, orient=HORIZONTAL, length=150)
        self.tab1_min_rating.grid(column=3, row=0, padx=5, pady=2, sticky=W)

        self.tab1_btn_apply_filters = Button(tab1, text="Apply filters", command=self.tab1_apply_filters)
        self.tab1_btn_apply_filters.grid(column=0, row=1, padx=5, pady=2, sticky=W)

        # data
        self.tab1_ratings = ttk.Treeview(tab1, columns=('country', 'variety', 'rating'))
        self.tab1_ratings_scrollbar = Scrollbar(tab1, orient=VERTICAL)
        self.tab1_ratings_scrollbar.config(command=self.tab1_ratings.yview)
        self.tab1_ratings_scrollbar.grid(row=3, column=4, sticky=N+S)

        self.tab1_ratings.heading('#0', text='brand')
        self.tab1_ratings.heading('#1', text='country')
        self.tab1_ratings.heading('#2', text='variety')
        self.tab1_ratings.heading('#3', text='rating')

        self.tab1_ratings.column('#0', stretch=YES)
        self.tab1_ratings.column('#1', stretch=YES)
        self.tab1_ratings.column('#2', stretch=YES)
        self.tab1_ratings.column('#3', stretch=YES)

        self.tab1_ratings.grid(row=3, columnspan=4, sticky=N+S+E+W)

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

            self.tab1_load_filter('brand', self.tab1_select_brand)
            self.tab1_load_filter('country', self.tab1_select_country)
            self.tab1_apply_filters()
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

    def tab1_load_filter(self, filter_name, obj):
        command = {'command': 'data',
                   'params': {
                       'data': filter_name
                   }}
        self.in_out_server.write(json.dumps(command) + "\n")
        self.in_out_server.flush()
        filter_values = json.loads(self.in_out_server.readline().rstrip('\n'))
        filter_values.insert(0, filter_name)
        obj['values'] = filter_values
        obj.set(filter_name)

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
            ratings = json.loads(self.in_out_server.readline().rstrip('\n'))
            self.load_table(ratings)
        except Exception as ex:
            print(ex)

    def load_table(self, data):
        [self.tab1_ratings.delete(record) for record in self.tab1_ratings.get_children()]
        print(data)
        for rating in data:
            kaka1 = rating
            kaka2 = rating['brand']
            self.tab1_ratings.insert('', index='end', text=rating['brand'], values=(rating['country'], rating['variety'], rating['rating']))
        # [self.tab1_ratings.insert('', values=(rt['brand'], rt['country'], rt['variety'], rt['rating'])) for rt in data]



root = Tk()
app = Window(root)
root.mainloop()
