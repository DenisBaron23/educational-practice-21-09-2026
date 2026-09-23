import re
import tkinter as tk
from tkinter import messagebox, ttk


PARTNER_TYPES = ("ЗАО", "ООО", "ИП", "АО", "ПАО")


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.window = None

        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<FocusOut>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, event=None):
        if self.window is not None:
            return

        self.window = tk.Toplevel(self.widget)
        self.window.overrideredirect(True)

        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.window.geometry(f"+{x}+{y}")

        tk.Label(
            self.window,
            text=self.text,
            background="#FFF4CC",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=5,
        ).pack()

    def hide(self, event=None):
        if self.window is not None:
            self.window.destroy()
            self.window = None


class PartnerEditWindow(tk.Toplevel):
    def __init__(self, parent, partner=None, on_save=None):
        super().__init__(parent)

        # Без id создаем запись, с id редактируем существующую.
        self.partner_id = None if partner is None else partner["id"]
        self.on_save = on_save
        self.saved = False

        self.variables = {}
        self.tooltips = []

        mode = "Добавление" if partner is None else "Редактирование"

        self.title(f"CRM: Карточка партнера [{mode}]")
        self.geometry("670x560")
        self.minsize(570, 520)
        self.transient(parent)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Escape>", self.cancel)

        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)

        ttk.Label(
            container,
            text="Карточка партнера",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 15),
        )

        fields = [
            ("name", "Наименование *"),
            ("partner_type", "Тип партнера"),
            ("rating", "Рейтинг"),
            ("address", "Адрес"),
            ("director", "ФИО директора"),
            ("phone", "Телефон"),
            ("email", "Email компании *"),
        ]

        for row, (key, label) in enumerate(fields, start=1):
            variable = tk.StringVar()
            self.variables[key] = variable

            ttk.Label(
                container,
                text=label,
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 15),
                pady=8,
            )

            if key == "partner_type":
                widget = ttk.Combobox(
                    container,
                    textvariable=variable,
                    values=PARTNER_TYPES,
                    state="readonly",
                )
            else:
                widget = ttk.Entry(
                    container,
                    textvariable=variable,
                )

            widget.grid(
                row=row,
                column=1,
                sticky="ew",
                pady=8,
            )

            if key == "phone":
                self.tooltips.append(
                    ToolTip(widget, "Пример: +7 (900) 123-45-67")
                )

            if key == "email":
                self.tooltips.append(
                    ToolTip(widget, "Пример: company@example.ru")
                )

        ttk.Label(
            container,
            text=(
                "* Обязательные поля\n"
                "Телефон: +7 (900) 123-45-67\n"
                "Email: company@example.ru"
            ),
        ).grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="w",
            pady=15,
        )

        buttons = ttk.Frame(container)
        buttons.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="e",
        )

        save_text = "Сохранить" if on_save is not None else "Проверить ввод"

        ttk.Button(
            buttons,
            text=save_text,
            command=self.save,
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons,
            text="Отмена",
            command=self.cancel,
        ).pack(side="left", padx=5)

        if partner is not None:
            for key, variable in self.variables.items():
                variable.set(str(partner[key]))

        # Снимок делаем после заполнения полей данными из базы.
        self.initial_state = self.snapshot()

    def snapshot(self):
        return {
            key: variable.get()
            for key, variable in self.variables.items()
        }

    def get_validated_data(self):
        data = {
            key: value.strip()
            for key, value in self.snapshot().items()
        }

        if not data["name"]:
            raise ValueError(
                "Наименование не должно быть пустым.\n"
                "Введите название партнера и повторите сохранение."
            )

        if not data["email"]:
            raise ValueError(
                "Email не должен быть пустым.\n"
                "Введите электронную почту компании."
            )

        if data["partner_type"] not in PARTNER_TYPES:
            raise ValueError(
                "Выберите тип партнера из выпадающего списка."
            )

        if re.fullmatch(r"[0-9]+", data["rating"]) is None:
            raise ValueError(
                "Рейтинг должен быть целым числом от 0.\n"
                "Удалите буквы, минус и знаки препинания."
            )

        try:
            rating = int(data["rating"])
        except ValueError as error:
            raise ValueError(
                "Рейтинг слишком длинный.\n"
                "Введите меньшее целое число."
            ) from error

        if rating > 9223372036854775807:
            raise ValueError(
                "Рейтинг превышает допустимый размер числа в базе.\n"
                "Введите меньшее значение."
            )

        data["rating"] = rating
        return data

    def save(self):
        try:
            data = self.get_validated_data()
        except ValueError as error:
            messagebox.showerror(
                "Ошибка ввода",
                str(error),
                parent=self,
            )
            return

        if self.on_save is None:
            messagebox.showinfo(
                "Проверка формы",
                "Поля заполнены корректно.\n"
                "Работа с базой подключается в задании 3.",
                parent=self,
            )
            return

        if self.on_save(self.partner_id, data):
            self.saved = True
            self.destroy()

    def cancel(self, event=None):
        self.destroy()
