from tkinter import *
from tkinter import ttk
from APM_ramen_ratings.data.RatingRepository import RatingRepository


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        ratings = RatingRepository()
        self.master.title("Ramen ratings")

        # configure tabs
        tab_control = ttk.Notebook(self.master)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text="all ratings")
        tab_control.add(tab2, text="brand popularity")

        # tab: all ratings
        ttk.Label(tab1, text="filters").grid(column=0, row=0, padx=10, pady=5)

        self.tab1_select_brand = StringVar(tab_control)
        self.tab1_select_brand.set("brand")
        BRANDS = ratings.get_brands()
        ttk.OptionMenu(tab1, self.tab1_select_brand, *BRANDS).grid(column=0, row=1, padx=10, pady=5)

        self.tab1_select_country = StringVar(tab_control)
        self.tab1_select_country.set("country")
        COUNTRIES = ratings.get_countries()
        ttk.OptionMenu(tab1, self.tab1_select_country, *COUNTRIES).grid(column=1, row=1, padx=10, pady=5)

        tab_control.pack(fill=BOTH, expand=1)


root = Tk()
app = Window(root)
# tab_control.pack(expand=1, fill="both")
root.mainloop()
