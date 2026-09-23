import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from db import get_partner, list_partners, save_partner
from partner_edit_window import PartnerEditWindow


def calculate_discount(quantity):
    if quantity < 10000:
        return 0

    if quantity < 50000:
        return 5

    if quantity < 300000:
        return 10

    return 15


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CRM: Реестр партнеров")
        self.geometry("1100x550")
        self.minsize(800, 400)

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

        ttk.Button(
            toolbar,
            text="Редактировать",
            command=self.open_selected,
        ).pack(side="right", padx=8)

        ttk.Button(
            toolbar,
            text="Обновить",
            command=self.refresh,
        ).pack(side="right")

        container = ttk.Frame(self, padding=(15, 0, 15, 15))
        container.pack(fill="both", expand=True)

        columns = (
            "type",
            "name",
            "rating",
            "director",
            "phone",
            "quantity",
            "discount",
        )

        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "type": ("Тип", 65),
            "name": ("Наименование", 170),
            "rating": ("Рейтинг", 65),
            "director": ("ФИО директора", 220),
            "phone": ("Телефон", 170),
            "quantity": ("Объем продаж", 100),
            "discount": ("Скидка", 65),
        }

        for key, (title, width) in headings.items():
            self.table.heading(key, text=title)
            self.table.column(key, width=width, minwidth=50)

        vertical = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.table.yview,
        )

        horizontal = ttk.Scrollbar(
            container,
            orient="horizontal",
            command=self.table.xview,
        )

        self.table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )

        self.table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.table.bind("<Double-1>", self.on_double_click)

        self.after_idle(self.refresh)

    def refresh(self):
        try:
            partners = list_partners()
        except sqlite3.Error:
            messagebox.showerror(
                "Ошибка загрузки",
                "Не удалось загрузить партнеров.\n\n"
                "При первом запуске выполните python init_db.py.\n"
                "Если база уже есть, проверьте доступ к app.db, "
                "затем нажмите «Обновить».\n\n"
                "Существующие данные не удаляйте.",
                parent=self,
            )
            return

        selected = self.table.selection()
        scroll_position = self.table.yview()[0]

        # Удаляем старые строки только после успешного чтения базы.
        for item in self.table.get_children():
            self.table.delete(item)

        for partner in partners:
            quantity = partner["total_quantity"]

            self.table.insert(
                "",
                "end",
                iid=str(partner["id"]),
                values=(
                    partner["partner_type"],
                    partner["name"],
                    partner["rating"],
                    partner["director"],
                    partner["phone"],
                    quantity,
                    f"{calculate_discount(quantity)}%",
                ),
            )

        if selected and self.table.exists(selected[0]):
            self.table.selection_set(selected[0])
            self.table.focus(selected[0])

        self.table.update_idletasks()
        self.table.yview_moveto(scroll_position)

    def open_add_window(self):
        self.open_editor()

    def on_double_click(self, event):
        row_id = self.table.identify_row(event.y)

        if row_id:
            self.open_editor(int(row_id))

    def open_selected(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                "Выбор партнера",
                "Выберите строку партнера в таблице.",
                parent=self,
            )
            return

        self.open_editor(int(selected[0]))

    def open_editor(self, partner_id=None):
        partner = None

        if partner_id is not None:
            try:
                partner = get_partner(partner_id)
            except ValueError as error:
                messagebox.showerror(
                    "Партнер не найден",
                    str(error),
                    parent=self,
                )
                return
            except sqlite3.Error:
                messagebox.showerror(
                    "Ошибка открытия карточки",
                    "Не удалось прочитать данные партнера.\n"
                    "Проверьте доступ к app.db и повторите попытку.",
                    parent=self,
                )
                return

        window = PartnerEditWindow(
            self,
            partner=partner,
            on_save=self.persist_partner,
        )

        window.wait_visibility()
        window.grab_set()
        self.wait_window(window)

        if window.saved:
            self.refresh()

    def persist_partner(self, partner_id, data):
        try:
            save_partner(partner_id, data)
        except ValueError as error:
            messagebox.showerror(
                "Ошибка сохранения",
                str(error),
                parent=self.grab_current() or self,
            )
            return False
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Ошибка целостности данных",
                "База отклонила запись.\n"
                "Проверьте обязательные поля, тип партнера и рейтинг.\n"
                "Если ошибка повторяется, проверьте схему базы данных.\n\n"
                "Введенные данные остались в карточке.",
                parent=self.grab_current() or self,
            )
            return False
        except sqlite3.Error:
            messagebox.showerror(
                "Ошибка базы данных",
                "Не удалось сохранить данные.\n\n"
                "Проверьте наличие app.db и права записи в папку.\n"
                "Если база занята другой программой, завершите "
                "ее операцию и повторите сохранение.\n\n"
                "Введенные данные остались в карточке.",
                parent=self.grab_current() or self,
            )
            return False

        return True
