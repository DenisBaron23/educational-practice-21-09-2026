from contextlib import contextmanager
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

PARTNER_TYPES = ("ЗАО", "ООО", "ИП", "АО", "ПАО")

FIELDS = (
    "name",
    "partner_type",
    "rating",
    "address",
    "director",
    "phone",
    "email",
)


@contextmanager
def connection():
    # mode=rw не позволяет незаметно создать пустую базу при ошибке пути.
    uri = DB_PATH.resolve().as_uri() + "?mode=rw"
    db = sqlite3.connect(uri, uri=True, timeout=3)

    try:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")

        with db:
            yield db
    finally:
        db.close()


def list_partners():
    with connection() as db:
        rows = db.execute(
            """
            SELECT
                p.*,
                COALESCE(
                    (
                        SELECT SUM(s.quantity)
                        FROM sales_history AS s
                        WHERE s.partner_id = p.id
                    ),
                    0
                ) AS total_quantity
            FROM partners AS p
            ORDER BY p.id
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_partner(partner_id):
    with connection() as db:
        row = db.execute(
            "SELECT * FROM partners WHERE id = ?",
            (partner_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            "Партнер больше не существует.\n"
            "Закройте карточку и обновите список."
        )

    return dict(row)


def save_partner(partner_id, data):
    if data["partner_type"] not in PARTNER_TYPES:
        raise ValueError("Выберите существующий тип партнера.")

    values = tuple(data[field] for field in FIELDS)

    with connection() as db:
        if partner_id is None:
            cursor = db.execute(
                """
                INSERT INTO partners (
                    name,
                    partner_type,
                    rating,
                    address,
                    director,
                    phone,
                    email
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            saved_id = cursor.lastrowid
        else:
            # Обновляем поля, но не id: связи с продажами остаются прежними.
            cursor = db.execute(
                """
                UPDATE partners
                SET
                    name = ?,
                    partner_type = ?,
                    rating = ?,
                    address = ?,
                    director = ?,
                    phone = ?,
                    email = ?
                WHERE id = ?
                """,
                values + (partner_id,),
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    "Не удалось обновить партнера: запись не найдена.\n"
                    "Закройте карточку и обновите список."
                )

            saved_id = partner_id

    return saved_id


def add_sale(partner_id, quantity):
    if type(quantity) is not int or quantity < 0:
        raise ValueError(
            "Количество должно быть целым неотрицательным числом."
        )

    with connection() as db:
        partner = db.execute(
            "SELECT id FROM partners WHERE id = ?",
            (partner_id,),
        ).fetchone()

        if partner is None:
            raise ValueError(
                "Нельзя добавить продажу несуществующему партнеру."
            )

        db.execute(
            """
            INSERT INTO sales_history (partner_id, quantity)
            VALUES (?, ?)
            """,
            (partner_id, quantity),
        )
