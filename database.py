import sqlite3

DB_NAME = 'globetrotter.db'


def get_db():
    """Return a database connection with row factory set."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all required tables."""
    conn = get_db()
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Trips table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            description TEXT,
            start_date  TEXT,
            end_date    TEXT,
            is_public   INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Activities table — M2
    c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT,
            duration    TEXT,
            cost        REAL    DEFAULT 0,
            city        TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Trip-Activities join table — M2
    c.execute('''
        CREATE TABLE IF NOT EXISTS trip_activities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id     INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            day_number  INTEGER DEFAULT 1,
            notes       TEXT,
            FOREIGN KEY (trip_id)     REFERENCES trips(id),
            FOREIGN KEY (activity_id) REFERENCES activities(id)
        )
    ''')

    conn.commit()
    conn.close()
    print('✅ Database initialized.')


if __name__ == '__main__':
    init_db()
