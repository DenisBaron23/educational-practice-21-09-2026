CREATE TABLE partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    partner_type TEXT NOT NULL
        CHECK (partner_type IN ('ЗАО', 'ООО', 'ИП', 'АО', 'ПАО')),

    rating INTEGER NOT NULL
        CHECK (typeof(rating) = 'integer' AND rating >= 0),

    address TEXT NOT NULL DEFAULT '',
    director TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',

    email TEXT NOT NULL
        CHECK (length(trim(email)) > 0)
);

CREATE TABLE sales_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    partner_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL
        CHECK (typeof(quantity) = 'integer' AND quantity >= 0),

    FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
);

CREATE INDEX idx_sales_partner
    ON sales_history(partner_id);

INSERT INTO partners (
    name,
    partner_type,
    rating,
    address,
    director,
    phone,
    email
)
VALUES
    (
        'Север',
        'ООО',
        10,
        'г. Москва, ул. Лесная, 1',
        'Иванов Иван Иванович',
        '+7 (900) 111-22-33',
        'sever@example.ru'
    ),
    (
        'Вектор',
        'ЗАО',
        8,
        'г. Казань, ул. Центральная, 5',
        'Петров Петр Петрович',
        '+7 (900) 222-33-44',
        'vector@example.ru'
    );

INSERT INTO sales_history (partner_id, quantity)
VALUES
    (1, 25000),
    (1, 25000),
    (2, 300000);
