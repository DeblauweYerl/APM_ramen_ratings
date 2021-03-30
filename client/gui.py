import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("tab widget")
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab_control.add(tab1, text="tab1")
tab_control.add(tab2, text="tab2")
ttk.Label(tab1, text="hey tab 1").grid(column=0, row=0, padx=30, pady=5)
ttk.Label(tab1, text="hey tab 1-2").grid(column=0, row=1, padx=30, pady=5)
ttk.Label(tab1, text="hey tab 1-3").grid(column=1, row=1, padx=30, pady=5)
tab_control.pack(expand=1, fill="both")
root.mainloop()