#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk

from ssr_monitor import ssr_monitor


class ssr_top:

    mon = ssr_monitor()
    curr_select_qpn = None

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("SSR top")
        self.root.geometry("")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        align_mode = "nswe"
        pad = 5

        self.div0 = tk.Frame(self.root)
        self.div1 = tk.Frame(self.root)
        self.div2 = tk.Frame(self.root)

        self.div0.grid(column=0, row=0, padx=pad, pady=pad, sticky=align_mode)
        self.div1.grid(column=0, row=1, padx=pad, pady=pad, sticky=align_mode)
        self.div2.grid(
            column=1, row=0, padx=pad, pady=pad, sticky=align_mode, rowspan=2
        )

        # QP List (Treeview)
        self.qp_list = ttk.Treeview(self.div0, show="headings", columns="QP")
        self.qp_list.column("QP", anchor="center")
        self.qp_list.heading("QP", text="QP")

        self.qp_list.grid(column=0, row=0, sticky=align_mode)
        self.qp_list.pack(fill=tk.BOTH)

        self.qp_list.bind("<<TreeviewSelect>>", self.qp_list_select)

        # Refresh Button
        self.refresh_button = tk.Button(self.div1, text="Refresh")
        self.refresh_button.pack(fill=tk.BOTH)

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
        self.counter_table.pack(fill=tk.BOTH)

        # Configure qp and counter size
        self.qp_list.configure(height=12)
        self.counter_table.configure(height=12 + 2)
    def start(self):
        self.clock()
        self.root.mainloop()

    def qp_list_refresh(self):
        for i in self.qp_list.get_children():
            self.qp_list.delete(i)
        for i in self.mon.get_qp_list():
            self.qp_list.insert("", "end", text=i, value=i)

    def qp_list_select(self, event):
        curItem = self.qp_list.item(self.qp_list.focus())
        old_qpn = self.curr_select_qpn
        try:
            self.curr_select_qpn = curItem["values"][0]
        except:
            self.curr_select_qpn = old_qpn
        self.counter_table_update()

    def counter_table_update(self):
        qpn = self.curr_select_qpn

        print("Current Select QPN = ", qpn)
        counter_dict = self.mon.get_qp_counters(qpn)

        if counter_dict:  # dict is not empty
            for i in self.counter_table.get_children():
                self.counter_table.delete(i)
            for key, val in counter_dict.items():
                self.counter_table.insert("", "end", values=[key, val])
        else:
            self.qp_list_refresh()

    def refresh_button_click(self, event):
        self.qp_list_refresh()

    def clock(self):
        print("Current Selection = " + self.curr_select_qpn.__str__())
        self.root.after(1000, self.clock)
        self.counter_table_update()


if __name__ == "__main__":
    top = ssr_top()
    top.start()
