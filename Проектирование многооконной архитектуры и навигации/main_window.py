import tkinter as tk
from tkinter import ttk

from partner_edit_window import PartnerEditWindow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CRM: Реестр партнеров")
        self.geometry("850x500")
        self.minsize(650, 400)

        toolbar = ttk.Frame(self, padding=15)
        toolbar.pack(fill="x")

        ttk.Label(
            toolbar,
            text="Реестр партнеров",
            font=("Arial", 17, "bold"),
        ).pack(side="left")

        ttk.Button(
            toolbar,
            text="Добавить партнера",
            command=self.open_add_window,
        ).pack(side="right")

        self.table = ttk.Treeview(
            self,
            columns=("type", "name", "rating"),
            show="headings",
            selectmode="browse",
        )

        self.table.heading("type", text="Тип")
        self.table.heading("name", text="Наименование")
        self.table.heading("rating", text="Рейтинг")

        self.table.column("type", width=100)
        self.table.column("name", width=400)
        self.table.column("rating", width=100)

        self.table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )

        self.table.insert(
            "",
            "end",
            values=("ООО", "Север", 10),
        )

        self.table.insert(
            "",
            "end",
            values=("ЗАО", "Вектор", 8),
        )

    def open_add_window(self):
        window = PartnerEditWindow(self)

        # Главное окно не пересоздается и сохраняет состояние списка.
        window.wait_visibility()
        window.grab_set()
        self.wait_window(window)
