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

from APM_ramen_ratings.data.RatingRepository import RatingRepository


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.server_connect()

    def init_window(self):
        self.master.title("Ramen ratings")
        self.pack(fill=BOTH, expand=1)

        # configure tabs
        tab_control = ttk.Notebook(self)

        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab4 = ttk.Frame(tab_control)
        tab5 = ttk.Frame(tab_control)

        self.tab2 = tab2

        tab_control.pack(fill=BOTH, expand=1)
        tab1.pack(fill=BOTH, expand=1)
        tab2.pack(fill=BOTH, expand=1)

        tab_control.add(tab1, text="all ratings")
        tab_control.add(tab2, text="popularity graph")
        tab_control.add(tab3, text="brand stats")
        tab_control.add(tab4, text="kaka")
        tab_control.add(tab5, text="search ramen")

        # tab1: all ratings

        # filters
        self.tab1_select_brand = ttk.Combobox(tab1)
        self.tab1_select_brand.grid(column=0, row=0, padx=(2, 10), pady=5, sticky=E + W)

        self.tab1_select_country = ttk.Combobox(tab1)
        self.tab1_select_country.grid(column=1, row=0, padx=(2, 10), pady=5, sticky=E + W)

        ttk.Label(tab1, text="min. rating:").grid(column=2, row=0, pady=5, sticky=E)
        self.tab1_min_rating = Scale(tab1, from_=0, to=5, tickinterval=5, orient=HORIZONTAL, length=150)
        self.tab1_min_rating.grid(column=3, row=0, padx=(10, 2), pady=5, sticky=E + W)

        tab1_btn_apply_filters = Button(tab1, text="Apply filters", command=self.tab1_apply_filters)
        tab1_btn_apply_filters.grid(column=0, row=1, padx=(2, 10), pady=5, sticky=W)

        # data
        columns_ratings = ('brand', 'country', 'variety', 'rating')
        self.tab1_ratings = ttk.Treeview(tab1, columns=columns_ratings, show='headings')
        self.tab1_ratings.grid(padx=(2, 0))
        tab1_ratings_scrollbar = Scrollbar(tab1, orient=VERTICAL)
        self.tab1_ratings.configure(yscrollcommand=tab1_ratings_scrollbar.set)
        tab1_ratings_scrollbar.config(command=self.tab1_ratings.yview)
        tab1_ratings_scrollbar.grid(row=3, column=4, padx=(0, 2), sticky=N + S)

        # for col in columns_ratings:
        #     self.tab1_ratings.heading(col, text=col, command=lambda: self.tab1_table_sort(self.tab1_ratings, col, False))

        self.tab1_ratings.heading('#1', text='brand')
        self.tab1_ratings.heading('#2', text='country')
        self.tab1_ratings.heading('#3', text='variety')
        self.tab1_ratings.heading('#4', text='rating')

        self.tab1_ratings.column('#1', stretch=YES)
        self.tab1_ratings.column('#2', stretch=YES)
        self.tab1_ratings.column('#3', stretch=YES)
        self.tab1_ratings.column('#4', stretch=YES)

        self.tab1_ratings.grid(row=3, columnspan=4, sticky=N + S + E + W)

        # tab2: popularity graph
        self.tab2_select_brand = ttk.Combobox(tab2)
        self.tab2_select_brand.grid(column=0, row=0, padx=10, pady=5, sticky=E + W)

        self.tab2_select_country = ttk.Combobox(tab2)
        self.tab2_select_country.grid(column=1, row=0, padx=10, pady=5, sticky=E + W)

        self.tab2_btn_apply_filters = Button(tab2, text="Apply filters", command=self.tab2_load_plot)
        self.tab2_btn_apply_filters.grid(column=0, row=1, padx=10, pady=5, sticky=W)

        # tab3: brand stats
        columns_brand_stats = ('brand', 'average rating', 'total ratings')
        self.tab3_brands = ttk.Treeview(tab3, columns=columns_brand_stats, show='headings')
        self.tab3_brands.grid(row=2, columnspan=4, sticky=N + S + E + W)
        tab3_brands_scrollbar = Scrollbar(tab3, orient=VERTICAL)
        self.tab3_brands.configure(yscrollcommand=tab3_brands_scrollbar.set)
        tab3_brands_scrollbar.config(command=self.tab3_brands.yview)
        tab3_brands_scrollbar.grid(row=2, column=4, padx=5, pady=5, sticky=N + S + W)

        # for col in columns_brand_stats:
        #     self.tab3_brands.heading(col, text=col, command=lambda: self.tab3_table_sort(self.tab3_brands, col, False))

        self.tab3_brands.heading('#1', text='brand')
        self.tab3_brands.heading('#2', text='average rating')
        self.tab3_brands.heading('#3', text='total ratings')

        self.tab3_brands.column('#1', stretch=YES)
        self.tab3_brands.column('#2', stretch=YES)
        self.tab3_brands.column('#3', stretch=YES)

        # tab5: search ramen
        self.tab5_searchbar = Entry(tab5)
        self.tab5_searchbar.grid(column=0, columnspan=3, padx=10, pady=20, sticky=E + W)
        tab5_btn_search = Button(tab5, text="Search", command=self.tab5_execute_search)
        tab5_btn_search.grid(row=0, column=3, padx=10, pady=20, sticky=E + W)

        # data
        self.tab5_ratings = ttk.Treeview(tab5, columns=columns_ratings, show='headings')
        self.tab5_ratings.grid(row=2, columnspan=4, sticky=N + S + E + W)
        tab5_ratings_scrollbar = Scrollbar(tab5, orient=VERTICAL)
        self.tab5_ratings.configure(yscrollcommand=tab5_ratings_scrollbar.set)
        tab5_ratings_scrollbar.config(command=self.tab5_ratings.yview)
        tab5_ratings_scrollbar.grid(row=2, column=4, padx=5, pady=5, sticky=N + S + W)

        # for col in columns_ratings:
        #     self.tab5_ratings.heading(col, text=col, command=lambda: self.tab5_table_sort(self.tab5_ratings, col, False))

        self.tab5_ratings.heading('#1', text='brand')
        self.tab5_ratings.heading('#2', text='country')
        self.tab5_ratings.heading('#3', text='variety')
        self.tab5_ratings.heading('#4', text='rating')

        self.tab5_ratings.column('#1', stretch=YES)
        self.tab5_ratings.column('#2', stretch=YES)
        self.tab5_ratings.column('#3', stretch=YES)
        self.tab5_ratings.column('#4', stretch=YES)

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

            # tab1
            self.load_filter('brand', self.tab1_select_brand)
            self.load_filter('country', self.tab1_select_country)
            self.tab1_apply_filters()

            # tab2
            self.load_filter('brand', self.tab2_select_brand)
            self.load_filter('country', self.tab2_select_country)
            self.tab2_load_plot()

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

    ### tab2 ###
    def tab2_load_plot(self):
        command = {'command': 'data',
                   'params': {
                       'data': 'all',
                       'filters': {
                           'brand': self.tab2_select_brand.get(),
                           'country': self.tab2_select_country.get(),
                           'min_rating': 0
                       }
                   }}

        self.in_out_server.write(json.dumps(command) + "\n")
        self.in_out_server.flush()
        ratings = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
        rating_scores = sorted([float(rt[5]) for rt in ratings])

        fig = plt.figure(figsize=(7, 3), facecolor='lightgrey', edgecolor='grey')

        plt.hist(rating_scores, bins=21)
        plt.xticks(np.arange(6), [0,1,2,3,4,5])

        canvas = FigureCanvasTkAgg(fig, self.tab2)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row=2, column=0, columnspan=7, padx=5, pady=5)

    ### tab3 ###
    def load_treeview_brand_stats(self, data, treeview_obj):
        [treeview_obj.delete(record) for record in treeview_obj.get_children()]
        [treeview_obj.insert('', index='end', values=(rt[1], rt[4], rt[2], rt[5])) for rt in data]

    ### tab5 ###
    def tab5_execute_search(self):
        command = {'command': 'data',
                   'params': {
                       'data': 'search',
                       'search': self.tab5_searchbar.get()
                   }}
        try:
            self.in_out_server.write(json.dumps(command) + "\n")
            self.in_out_server.flush()
            ratings = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
            self.load_treeview_ratings(ratings, self.tab5_ratings)
        except Exception as ex:
            print(ex)



root = Tk()
app = Window(root)
root.mainloop()
