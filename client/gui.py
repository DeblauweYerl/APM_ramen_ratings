from tkinter import *
from tkinter import ttk
from APM_ramen_ratings.data.RatingRepository import RatingRepository

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.ratings = RatingRepository()
        self.init_window()

    def init_window(self):
        self.master.title("Ramen ratings")

        # configure tabs
        tab_control = ttk.Notebook(self.master)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text="all ratings")
        tab_control.add(tab2, text="brand popularity")

        # tab: all ratings
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

        self.tab1_btn_apply_filters = Button(tab1, text="Apply filters", command=self.apply_filters)
        self.tab1_btn_apply_filters.grid(column=0, row=2, padx=15, pady=2)

        # data visualisation


        tab_control.pack(fill=BOTH, expand=1)

    def apply_filters(self):
        # filters = {'brand': self.tab1_select_brand.get(),
        #            'country': self.tab1_select_country.get(),
        #            'min_rating': self.tab1_min_rating.get()}
        # print([rt.review_number for rt in self.ratings.get_filtered_ratings(filters)])
        pass


root = Tk()
app = Window(root)
# tab_control.pack(expand=1, fill="both")
root.mainloop()
