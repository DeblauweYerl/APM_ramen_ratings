from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import logging
import socket
import jsonpickle

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

        # configure tabs
        tab_control = ttk.Notebook(self.master)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text="all ratings")
        tab_control.add(tab2, text="brand popularity")

        # tab1: all ratings
        # filters
        # Label(tab1, text="filters").grid(column=0, row=0, padx=10, pady=2)

        brands = self.ratings.get_brands()
        brands.insert(0, 'brand')
        self.tab1_select_brand = ttk.Combobox(tab1, values=brands)
        self.tab1_select_brand.grid(column=0, row=1, padx=15, pady=2)
        self.tab1_select_brand.set(brands[0])

        countries = self.ratings.get_countries()
        countries.insert(0, 'country')
        self.tab1_select_country = ttk.Combobox(tab1, values=countries)
        self.tab1_select_country.grid(column=1, row=1, padx=15, pady=2)
        self.tab1_select_country.set(countries[0])

        ttk.Label(tab1, text="min. rating").grid(column=2, row=1, padx=5, pady=2)
        self.tab1_min_rating = Scale(tab1, from_=0, to=5, tickinterval=5, orient=HORIZONTAL, length=150)
        self.tab1_min_rating.grid(column=3, row=1, padx=15, pady=2)

        self.tab1_btn_apply_filters = Button(tab1, text="Apply filters", command=self.tab1_apply_filters)
        self.tab1_btn_apply_filters.grid(column=0, row=2, padx=15, pady=2)

        # data visualisation*-

        tab_control.pack(fill=BOTH, expand=1)


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


    def tab1_apply_filters(self):
        filters = {'brand': self.tab1_select_brand.get(),
                   'country': self.tab1_select_country.get(),
                   'min_rating': self.tab1_min_rating.get()}
        command = "/data all " + str(filters).replace(" ", "")

        self.in_out_server.write(jsonpickle.encode(command) +"\n")
        self.in_out_server.flush()
        ratings = self.in_out_server.readline().rstrip('\n')
        self.load_table(jsonpickle.decode(ratings))

    def load_table(self, data):
        pass


root = Tk()
app = Window(root)
# tab_control.pack(expand=1, fill="both")
root.mainloop()
