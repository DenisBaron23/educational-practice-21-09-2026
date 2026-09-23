import sqlite3

from db import BASE_DIR, DB_PATH


def main():
    if DB_PATH.exists():
        print("База уже существует. Данные не изменены.")
        return

    try:
        schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")

        db = sqlite3.connect(DB_PATH)

        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.executescript("BEGIN;\n" + schema + "\nCOMMIT;")
        except sqlite3.Error:
            db.rollback()
            raise
        finally:
            db.close()

    except (sqlite3.Error, OSError) as error:
        print(f"Ошибка создания базы: {error}")
        print(
            "Если появился неполный app.db, удалите только этот новый "
            "учебный файл перед повторной попыткой."
        )
        raise SystemExit(1) from error

    print(f"База создана: {DB_PATH}")


if __name__ == "__main__":
    main()

