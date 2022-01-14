#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

from ssr_monitor import ssr_monitor

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")

import numpy as np


class ssr_top:

    mon = ssr_monitor()
    curr_select_qpn = None
    curr_select_counter = None
    counter_dict = {}

    def __init__(self) -> None:
        self.root = ThemedTk(theme='adapta')
        self.root.title("SSR top")
        self.root.geometry("")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
        align_mode = "nswe"
        pad = 5

        self.div0 = ttk.Frame(self.root)
        self.div1 = ttk.Frame(self.root)
        self.div2 = ttk.Frame(self.root)
        self.div3 = ttk.Frame(self.root)

        self.div0.grid(column=0, row=0, padx=pad, pady=pad, sticky=align_mode)
        self.div1.grid(column=0, row=1, padx=pad, pady=pad, sticky=align_mode)
        self.div2.grid(
            column=1, row=0, padx=pad, pady=pad, sticky=align_mode, rowspan=2
        )
        self.div3.grid(
            column=0, row=2, padx=pad, pady=pad, sticky=align_mode, columnspan=2
        )

        # QP List (Treeview)
        self.qp_list = ttk.Treeview(self.div0, show="headings", columns="QP")
        self.qp_list.column("QP", anchor="center")
        self.qp_list.heading("QP", text="QP")

        self.qp_list.grid(column=0, row=0, sticky=align_mode)
        self.qp_list.pack(fill=tk.BOTH, expand=1)

        self.qp_list.bind("<<TreeviewSelect>>", self.qp_list_select)

        # Refresh Button
        self.refresh_button = ttk.Button(self.div1, text="Refresh")
        self.refresh_button.pack(fill=tk.BOTH, expand=1)

        self.refresh_button.bind("<Button>", self.refresh_button_click)

        # Counter Table
        self.counter_table = ttk.Treeview(
            self.div2, show="headings", columns=["counter", "value"]
        )
        self.counter_table.column("counter", anchor="center")
        self.counter_table.column("value", anchor="center")
        self.counter_table.heading("counter", text="counter")
        self.counter_table.heading("value", text="value")

        self.counter_table.grid(column=0, row=0, sticky=align_mode)
        self.counter_table.pack(fill=tk.BOTH, expand=1)

        self.counter_table.bind("<<TreeviewSelect>>", self.counter_table_select)

        # Configure qp and counter size
        self.qp_list.configure(height=12)
        self.counter_table.configure(height=12 + 2)

        # Canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure_plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.div3)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def start(self):
        self.clock()
        self.root.mainloop()

    def qp_list_refresh(self):
        for i in self.qp_list.get_children():
            self.qp_list.delete(i)
        for live_qp in self.mon.get_qp_list():
            self.qp_list.insert("", "end", text=live_qp, values=[live_qp])

    def qp_list_select(self, event):
        curItem = self.qp_list.item(self.qp_list.focus())
        old_qpn = self.curr_select_qpn
        try:
            self.curr_select_qpn = curItem["values"][0]
        except:
            self.curr_select_qpn = old_qpn
        self.counter_table_display()

    def counter_table_display(self):
        if self.curr_select_qpn == None:
            return

        qpn = int(self.curr_select_qpn)
        if qpn in self.counter_dict:
            for i in self.counter_table.get_children():
                self.counter_table.delete(i)
            for key, val in self.counter_dict[qpn].items():
                self.counter_table.insert("", "end", values=[key, val[-1]])

    def counter_dict_update(self):
        for qpn in self.mon.get_qp_list():
            qpn = int(qpn)
            tmp = self.mon.get_qp_counters(qpn)
            if tmp:  # dict is not empty
                if qpn not in self.counter_dict:
                    self.counter_dict[qpn] = {}

                for key, val in tmp.items():
                    if key not in self.counter_dict[qpn]:
                        self.counter_dict[qpn][key] = np.zeros(128, dtype=int)

                    self.counter_dict[qpn][key] = np.roll(self.counter_dict[qpn][key], -1)
                    self.counter_dict[qpn][key][-1] = val

    def counter_table_select(self, event):
        curItem = self.counter_table.item(self.counter_table.focus())
        old_counter = self.curr_select_counter
        try:
            self.curr_select_counter = curItem["values"][0]
        except:
            self.curr_select_counter = old_counter
        self.canvas_display()

    def canvas_display(self):
        if self.curr_select_qpn == None:
            return
        if self.curr_select_counter == None:
            return

        qpn = int(self.curr_select_qpn)
        counter = self.curr_select_counter
        title = "%d: %s"%(qpn, counter)
        self.figure_plot.clear()
        self.figure_plot.plot(
            np.arange(-128, -0),
            self.counter_dict[qpn][counter],
        )
        self.figure_plot.set_title(title)
        self.figure_plot.set_xlabel("second")
        self.figure_plot.set_ylabel("times")
        self.canvas.draw()


    def refresh_button_click(self, event):
        self.qp_list_refresh()

    def clock(self):
        self.root.after(1000, self.clock)
        self.counter_dict_update()
        self.counter_table_display()
        self.canvas_display()


if __name__ == "__main__":
    top = ssr_top()
    top.start()
