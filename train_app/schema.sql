CREATE TABLE IF NOT EXISTS operator (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_id INTEGER NOT NULL,
    ppm INT NOT NULL,
    record_date TEXT NOT NULL,
    record_time TEXT NOT NULL,
    FOREIGN KEY (operator_id) REFERENCES operator (id)
);
