import os
import sqlite3

DB_NAME = os.getenv('DATABASE_URL', 'globetrotter.db')


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

    # Multi-city trip stops table — M3
    c.execute('''
        CREATE TABLE IF NOT EXISTS trip_stops (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id     INTEGER NOT NULL,
            city        TEXT    NOT NULL,
            country     TEXT,
            start_date  TEXT,
            end_date    TEXT,
            stop_order  INTEGER DEFAULT 1,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        )
    ''')

    # Activities table — M1/M2
    c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT    NOT NULL,
            category       TEXT    NOT NULL,
            description    TEXT,
            duration       TEXT,
            cost           REAL    DEFAULT 0,
            city           TEXT,
            preferred_time TEXT,
            image_url      TEXT,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migration checks for columns
    try:
        c.execute('ALTER TABLE activities ADD COLUMN preferred_time TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE activities ADD COLUMN image_url TEXT')
    except sqlite3.OperationalError:
        pass

    # Trip-Activities join table — M1/M2/M3
    c.execute('''
        CREATE TABLE IF NOT EXISTS trip_activities (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id       INTEGER NOT NULL,
            activity_id   INTEGER NOT NULL,
            stop_id       INTEGER,
            day_number    INTEGER DEFAULT 1,
            activity_date TEXT,
            activity_time TEXT,
            notes         TEXT,
            FOREIGN KEY (trip_id)     REFERENCES trips(id),
            FOREIGN KEY (activity_id) REFERENCES activities(id),
            FOREIGN KEY (stop_id)     REFERENCES trip_stops(id)
        )
    ''')

    # Migration checks for trip_activities columns
    try:
        c.execute('ALTER TABLE trip_activities ADD COLUMN stop_id INTEGER')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE trip_activities ADD COLUMN activity_time TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE trip_activities ADD COLUMN activity_date TEXT')
    except sqlite3.OperationalError:
        pass

    # Trip Expenses Table — M1 Turn 5 Budget Engine
    c.execute('''
        CREATE TABLE IF NOT EXISTS trip_expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id     INTEGER NOT NULL,
            category    TEXT    NOT NULL,
            title       TEXT    NOT NULL,
            cost        REAL    NOT NULL DEFAULT 0,
            notes       TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        )
    ''')

    conn.commit()

    # Seed initial high-quality demo dataset if empty or missing Kashmir
    c.execute("SELECT COUNT(*) FROM activities WHERE LOWER(city) = 'kashmir'")
    if c.fetchone()[0] == 0:
        demo_activities = [
            ('Dal Lake Shikara Ride & Houseboat', 'Experience', 'Scenic boat ride across Dal Lake with views of snow-capped Zabarwan range.', '2.0 hrs', 2000.0, 'Kashmir', '08:30 AM', '/static/images/kashmir.jpg'),
            ('Gulmarg Gondola & Alpine Meadow', 'Adventure', 'World\'s highest cable car ride up to Apharwat Peak with pristine snow slopes.', '4.0 hrs', 3500.0, 'Kashmir', '10:00 AM', '/static/images/kashmir.jpg'),
            ('Pahalgam Valley & Betaab Tour', 'Nature', 'Explore lush pine forests, Lidder River streams, and breathtaking valley vistas.', '5.0 hrs', 2500.0, 'Kashmir', '09:00 AM', '/static/images/kashmir.jpg'),
            ('Eiffel Tower Summit Tour', 'Sightseeing', 'Iconic iron grid tower on the Champ de Mars offering panoramic city views.', '2.5 hrs', 3000.0, 'Paris', '09:00 AM', '/static/images/paris.jpg'),
            ('Louvre Museum Guided Tour', 'Culture', 'Explore Mona Lisa and thousands of world-famous masterworks.', '3.0 hrs', 4000.0, 'Paris', '10:30 AM', '/static/images/paris.jpg'),
            ('Colosseum & Roman Forum Tour', 'Culture', 'Step back in time inside the ancient amphitheater of Rome.', '3.0 hrs', 4200.0, 'Rome', '09:30 AM', '/static/images/rome.jpg'),
            ('Trevi Fountain & City Walking', 'Sightseeing', 'Discover Trevi Fountain, Pantheon, and Piazza Navona.', '2.0 hrs', 1500.0, 'Rome', '04:00 PM', '/static/images/rome.jpg'),
            ('Baga Beach & Sunset Water Sports', 'Adventure', 'Parasailing, jet ski, and relaxing beach vibes in North Goa.', '3.0 hrs', 2500.0, 'Goa', '03:30 PM', '/static/images/goa.jpg'),
            ('Hawa Mahal & Amber Fort Heritage Tour', 'Culture', 'Explore the iconic pink sandstone Palace of Winds and royal Amber Fort.', '4.0 hrs', 1800.0, 'Jaipur', '09:30 AM', '/static/images/jaipur.jpg')
        ]
        c.executemany('''
            INSERT INTO activities (name, category, description, duration, cost, city, preferred_time, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', demo_activities)
        conn.commit()

    # Convert existing low costs (< 200) to INR in database
    c.execute('UPDATE activities SET cost = cost * 80 WHERE cost > 0 AND cost < 200')
    c.execute('UPDATE trip_expenses SET cost = cost * 80 WHERE cost > 0 AND cost < 200')
    conn.commit()

    conn.close()
    print('[OK] Database initialized with Indian Rupee (INR) costs.')


if __name__ == '__main__':
    init_db()
