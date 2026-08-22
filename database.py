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

    # Activities table — M1/M2 (Name, Description, Category, Duration, Cost, City, Preferred Time)
    c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT,
            duration    TEXT,
            cost        REAL    DEFAULT 0,
            city        TEXT,
            preferred_time TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migration check for activities.preferred_time column
    try:
        c.execute('ALTER TABLE activities ADD COLUMN preferred_time TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Trip-Activities join table — M1/M2
    c.execute('''
        CREATE TABLE IF NOT EXISTS trip_activities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id     INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            stop_id     INTEGER,
            day_number  INTEGER DEFAULT 1,
            activity_time TEXT,
            notes       TEXT,
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

    conn.commit()

    # Seed initial high-quality demo dataset if empty
    cursor = c.execute('SELECT COUNT(*) FROM activities')
    if cursor.fetchone()[0] == 0:
        demo_activities = [
            ('Eiffel Tower Summit Tour', 'Sightseeing', 'Iconic iron grid tower on the Champ de Mars offering panoramic city views.', '2.5 hrs', 35.0, 'Paris', '09:00 AM'),
            ('Louvre Museum Guided Tour', 'Culture', 'Explore Mona Lisa and thousands of world-famous masterworks.', '3.0 hrs', 45.0, 'Paris', '10:30 AM'),
            ('Paris Gourmet Food Tour', 'Experience', 'Taste authentic croissants, artisan cheeses, and fine wines.', '3.5 hrs', 75.0, 'Paris', '01:00 PM'),
            ('Colosseum & Roman Forum Tour', 'Culture', 'Step back in time inside the ancient amphitheater of Rome.', '3.0 hrs', 50.0, 'Rome', '09:30 AM'),
            ('Rome City Walking Tour', 'Sightseeing', 'Discover Trevi Fountain, Pantheon, and Piazza Navona.', '2.0 hrs', 20.0, 'Rome', '04:00 PM'),
            ('Trastevere Evening Food Tour', 'Experience', 'Sample traditional pasta, gelato, and Italian wines.', '3.0 hrs', 65.0, 'Rome', '06:30 PM'),
            ('Sensoji Temple & Asakusa Walking Tour', 'Culture', 'Tokyo\'s oldest ancient Buddhist temple and historic shopping street.', '2.0 hrs', 15.0, 'Tokyo', '10:00 AM'),
            ('Tokyo Street Food Crawl', 'Experience', 'Yakitori, ramen, and matcha desserts in vibrant Shinjuku.', '3.0 hrs', 55.0, 'Tokyo', '05:30 PM'),
            ('Sagrada Familia Fast-Track Tour', 'Culture', 'Gaudí\'s unfinished masterpiece cathedral in Barcelona.', '2.0 hrs', 38.0, 'Barcelona', '11:00 AM'),
            ('London Eye & Thames Cruise', 'Sightseeing', 'Giant ferris wheel experience paired with scenic river sights.', '2.5 hrs', 42.0, 'London', '02:00 PM')
        ]
        c.executemany('''
            INSERT INTO activities (name, category, description, duration, cost, city, preferred_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', demo_activities)
        conn.commit()

    conn.close()
    print('[OK] Database initialized with column migrations.')


if __name__ == '__main__':
    init_db()
