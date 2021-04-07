import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from PIL import Imager k, Image
import pymysql
import os
import shutil
import g
form = tk.Tk()
form.title ("Tkinter Database Form")
form.geometry("50Ox280")
tab_parent = ttk.Notebook(form)
tabl = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab_parent.add(tabl, "Records")
tab_parent.add(tab2, "New Record")
tab_parent.pack(expand—I, fill= 'both')
form. main Loop