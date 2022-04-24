# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 06:50:12 2021

@author: hungd
"""

import tkinter as tk
from tkinter import filedialog

def fileDialogBox(initialdir="/", title="Select a File", filetypes="*.csv"):
    # Select File
    root=tk.Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()
    filename = filedialog.askopenfilename(initialdir=initialdir,
                                          title=title,
                                          filetypes = ((filetypes, filetypes),
                                                       ("all files", "*.*")))
    root.destroy()

    return filename