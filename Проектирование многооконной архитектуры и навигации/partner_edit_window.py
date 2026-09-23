import tkinter as tk
from tkinter import ttk


class PartnerEditWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("CRM: Карточка партнера [Добавление]")
        self.geometry("500x250")
        self.transient(parent)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", self.cancel)

        container = ttk.Frame(self, padding=25)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Карточка нового партнера",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            container,
            text="Поля карточки добавляются во втором задании.",
        ).pack(anchor="w", pady=20)

        ttk.Button(
            container,
            text="Назад",
            command=self.cancel,
        ).pack(anchor="e")

    def cancel(self, event=None):
        self.destroy()

