from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from APM_ramen_ratings.models.Account import Account

import logging
import socket
import jsonpickle
import json

### app ###
class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.server_connect()
        self.master.protocol("WM_DELETE_WINDOW", self.server_disconnect)

    def init_window(self):
        self.master.title(f"Ramen ratings - {self.nickname}")
        self.pack(fill=BOTH, expand=1)

        # configure tabs
        tab_control = ttk.Notebook(self)

        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab4 = ttk.Frame(tab_control)
        tab5 = ttk.Frame(tab_control)

        self.tab2 = tab2
        self.tab4 = tab4

        tab_control.pack(fill=BOTH, expand=1)
        tab1.pack(fill=BOTH, expand=1)
        tab2.pack(fill=BOTH, expand=1)
        tab3.pack(fill=BOTH, expand=1)
        tab4.pack(fill=BOTH, expand=1)
        tab5.pack(fill=BOTH, expand=1)

        tab_control.add(tab1, text="all ratings")
        tab_control.add(tab2, text="popularity graph")
        tab_control.add(tab3, text="brand stats")
        tab_control.add(tab4, text="compare brands/countries")
        tab_control.add(tab5, text="search ramen")

        # tab1: all ratings

        # grid config
        tab1.rowconfigure(2, weight=4)
        tab1.columnconfigure(4, weight=1)

        # filters
        self.tab1_select_brand = ttk.Combobox(tab1, height=25, state='readonly')
        self.tab1_select_brand.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=E + W)

        self.tab1_select_country = ttk.Combobox(tab1, height=25, state='readonly')
        self.tab1_select_country.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky=E + W)

        ttk.Label(tab1, text="min. rating:").grid(row=0, column=2, padx=(20, 0), pady=(10, 0), sticky=E)
        self.tab1_min_rating = Scale(tab1, from_=0, to=5, tickinterval=5, orient=HORIZONTAL, length=150)
        self.tab1_min_rating.grid(row=0, column=3, padx=5, pady=(10, 0), sticky=E + W)

        tab1_btn_apply_filters = Button(tab1, text="Apply filters", command=self.tab1_apply_filters)
        tab1_btn_apply_filters.grid(row=1, column=0, padx=10, pady=(0, 40), sticky=W)

        # data
        columns_ratings = ('brand', 'country', 'variety', 'rating')
        self.tab1_ratings = ttk.Treeview(tab1, columns=columns_ratings, show='headings')
        self.tab1_ratings.grid(row=2, column=0, columnspan=5, sticky=N + S + E + W)
        tab1_ratings_scrollbar = Scrollbar(tab1, orient=VERTICAL)
        self.tab1_ratings.configure(yscrollcommand=tab1_ratings_scrollbar.set)
        tab1_ratings_scrollbar.config(command=self.tab1_ratings.yview)
        tab1_ratings_scrollbar.grid(row=2, column=5, sticky=N + S + W)

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

        # tab2: popularity brands/countries

        # grid config
        tab2.rowconfigure(2, weight=1)
        tab2.columnconfigure(2, weight=1)

        # filters
        self.tab2_select_brand = ttk.Combobox(tab2, height=25, state='readonly')
        self.tab2_select_brand.grid(column=0, row=0, padx=10, pady=(20, 5), sticky=E + W)

        self.tab2_select_country = ttk.Combobox(tab2, height=25, state='readonly')
        self.tab2_select_country.grid(column=1, row=0, padx=10, pady=(20, 5), sticky=E + W)

        self.tab2_btn_apply_filters = Button(tab2, text="Apply filters", command=self.tab2_load_plot)
        self.tab2_btn_apply_filters.grid(column=0, row=1, padx=10, pady=(10, 40), sticky=W)

        # tab3: brand stats

        # grid config
        tab3.rowconfigure(0, weight=1)
        tab3.columnconfigure(0, weight=1)

        # table
        columns_brand_stats = ('brand', 'average rating', 'total ratings')
        self.tab3_brands = ttk.Treeview(tab3, columns=columns_brand_stats, show='headings')
        self.tab3_brands.grid(padx=(0), pady=(10, 0), sticky=N + S + E + W)
        tab3_brands_scrollbar = Scrollbar(tab3, orient=VERTICAL)
        self.tab3_brands.configure(yscrollcommand=tab3_brands_scrollbar.set)
        tab3_brands_scrollbar.config(command=self.tab3_brands.yview)
        tab3_brands_scrollbar.grid(row=0, column=1, padx=(0), pady=(0, 10), sticky=N + S + W)

        # for col in columns_brand_stats:
        #     self.tab3_brands.heading(col, text=col, command=lambda: self.tab3_table_sort(self.tab3_brands, col, False))

        self.tab3_brands.heading('#1', text='brand')
        self.tab3_brands.heading('#2', text='average rating')
        self.tab3_brands.heading('#3', text='total ratings')

        self.tab3_brands.column('#1', stretch=YES)
        self.tab3_brands.column('#2', stretch=YES)
        self.tab3_brands.column('#3', stretch=YES)

        # tab4: compare brands/countries

        # grid config
        tab4.rowconfigure(3, weight=1)
        tab4.columnconfigure(0, weight=1)
        tab4.columnconfigure(3, weight=1)

        # parameters
        self.tab4_radio_value = StringVar(tab4, "brand")
        tab4_radio_brands = Radiobutton(tab4, text='brand', variable=self.tab4_radio_value, value='brand',
                                        indicator=0, width=20, command=self.tab4_load_selects)
        tab4_radio_countries = Radiobutton(tab4, text='country', variable=self.tab4_radio_value, value='country',
                                           indicator=0, width=20, command=self.tab4_load_selects)
        tab4_radio_brands.grid(row=0, column=1, pady=(20, 5))
        tab4_radio_countries.grid(row=0, column=2, pady=(20, 5))
        tab4_radio_brands.select()

        self.tab4_compare1_select = ttk.Combobox(tab4, height=25, state='readonly')
        self.tab4_compare1_select.grid(row=1, column=1, padx=10, pady=5, sticky=E + W)

        Button(tab4, text='Compare', command=self.tab4_load_plots, width=14) \
            .grid(row=2, column=1, columnspan=2, padx=10, pady=(5, 40), sticky=E + W)

        self.tab4_compare2_select = ttk.Combobox(tab4, height=25, state='readonly')
        self.tab4_compare2_select.grid(row=1, column=2, padx=10, pady=5, sticky=E + W)

        # tab5: search ramen

        # grid config
        tab5.rowconfigure(2, weight=1)
        tab5.columnconfigure(3, weight=1)

        # searchbar
        self.tab5_searchbar = Entry(tab5, width=50)
        self.tab5_searchbar.grid(column=0, columnspan=2, padx=10, pady=(20, 40), sticky=E + W)
        tab5_btn_search = Button(tab5, text="Search", width=10, command=self.tab5_execute_search)
        tab5_btn_search.grid(row=0, column=2, padx=10, pady=(20, 40), sticky=E + W)

        # data
        self.tab5_ratings = ttk.Treeview(tab5, columns=columns_ratings, show='headings')
        self.tab5_ratings.grid(row=2, column=0, columnspan=4, sticky=N + S + E + W)
        tab5_ratings_scrollbar = Scrollbar(tab5, orient=VERTICAL)
        self.tab5_ratings.configure(yscrollcommand=tab5_ratings_scrollbar.set)
        tab5_ratings_scrollbar.config(command=self.tab5_ratings.yview)
        tab5_ratings_scrollbar.grid(row=2, column=4, pady=(0, 10), sticky=N + S + W)

        # for col in columns_ratings:
        #     self.tab5_ratings.heading(col, text=col, command=lambda: self.tab5_table_sort(self.tab5_ratings, col, False))

        self.tab5_ratings.heading('#1', text='brand')
        self.tab5_ratings.heading('#2', text='country')
        self.tab5_ratings.heading('#3', text='variety')
        self.tab5_ratings.heading('#4', text='rating')

        self.tab5_ratings.column('#1', width=150, stretch=YES)
        self.tab5_ratings.column('#2', width=120, stretch=YES)
        self.tab5_ratings.column('#3', width=450, stretch=YES)
        self.tab5_ratings.column('#4', width=60, stretch=YES)

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

            self.init_tabs()

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("RamenRatings - error", "Cannot connect to server.")

    def server_disconnect(self):
        try:
            logging.info("Close connection with server...")
            self.in_out_server.write("CLOSE\n")
            self.in_out_server.flush()
            self.s.close()
            self.master.destroy()
        except Exception as ex:
            logging.error("Foutmelding:close connection with server failed")

    ### general ###
    def save_login(self, nickname, name, email):
        command = {'command': 'save_account',
                   'params': {
                       'nickname': nickname,
                       'name': name,
                       'email': email
                   }}
        try:
            self.in_out_server.write(json.dumps(command) + "\n")
            self.in_out_server.flush()
            ratings = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
            self.load_treeview_ratings(ratings, self.tab1_ratings)
        except Exception as ex:
            print(ex)

    def init_tabs(self):
        self.init_tab1()
        self.init_tab2()
        self.tab3_load_treeview()
        self.init_tab4()

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

    ### tab2 ###
    def init_tab2(self):
        self.load_filter('brand', self.tab2_select_brand)
        self.load_filter('country', self.tab2_select_country)
        self.tab2_load_plot()

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

        fig = plt.figure(facecolor='white')

        plt.hist(rating_scores, bins=21)
        plt.xticks(np.arange(6), [0, 1, 2, 3, 4, 5])

        canvas = FigureCanvasTkAgg(fig, self.tab2)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=N + S + E + W)

    ### tab3 ###
    def tab3_load_treeview(self):
        command = {'command': 'data',
                   'params': {
                       'data': 'brand_stats'
                   }}
        self.in_out_server.write(json.dumps(command) + "\n")
        self.in_out_server.flush()
        brand_stats = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
        [self.tab3_brands.delete(record) for record in self.tab3_brands.get_children()]
        [self.tab3_brands.insert('', index='end',
                                 values=(brand, brand_stats[brand]['avg'], brand_stats[brand]['total'])) for brand in
         brand_stats]

    ### tab4 ###
    def init_tab4(self):
        self.tab4_load_selects()
        self.tab4_load_plots()

    def tab4_load_selects(self):
        self.load_filter(self.tab4_radio_value.get(), self.tab4_compare1_select)
        self.load_filter(self.tab4_radio_value.get(), self.tab4_compare2_select)

    def tab4_load_plots(self):
        command = {'command': 'data',
                   'params': {
                       'data': 'all',
                       'filters': {
                           'brand': 'brand',
                           'country': 'country',
                           'min_rating': 0
                       }
                   }}

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
        rating_scores = []

        for selection in [self.tab4_compare1_select.get(), self.tab4_compare2_select.get()]:
            if self.tab4_radio_value.get() == 'brand':
                command['params']['filters']['brand'] = selection
            else:
                command['params']['filters']['country'] = selection

            self.in_out_server.write(json.dumps(command) + "\n")
            self.in_out_server.flush()
            ratings = jsonpickle.decode(self.in_out_server.readline().rstrip('\n'))
            rating_scores.append(sorted([float(rt[5]) for rt in ratings]))

        ax1.set_title(self.tab4_compare1_select.get())
        ax1.boxplot(rating_scores[0])
        ax2.set_title(self.tab4_compare2_select.get())
        ax2.boxplot(rating_scores[1])
        for ax in [ax1, ax2]:
            ax.set_ylim([-0.5, 5.5])
            ax.set_xticks([])

        # fig = plt.figure(figsize=(7, 3), facecolor='lightgrey', edgecolor='grey')
        #
        # plt.hist(rating_scores, bins=21)
        # plt.xticks(np.arange(6), [0, 1, 2, 3, 4, 5])

        canvas = FigureCanvasTkAgg(fig, self.tab4)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky=N + S)

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
# login = Login(root)
app = Window(root)
root.mainloop()
