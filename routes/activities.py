from flask import Blueprint, request, jsonify
from database import get_db

activities_bp = Blueprint('activities', __name__)

# ── High Quality Seed Dataset ──────────────────────────────────
SAMPLE_ACTIVITIES = [
    ('Eiffel Tower Summit Tour',      'Sightseeing', 'Iconic iron grid tower on Champ de Mars offering panoramic city views.', '2.5 hours', 35.0, 'Paris', '09:00 AM'),
    ('Louvre Museum Guided Tour',     'Culture',     "Explore Mona Lisa and thousands of world-famous masterworks.",          '3 hours',   45.0, 'Paris', '10:30 AM'),
    ('Paris Gourmet Food Tour',        'Experience',  'Taste authentic croissants, artisan cheeses, and fine French wines.',    '3.5 hours', 75.0, 'Paris', '01:00 PM'),
    ('Colosseum & Forum Tour',        'Culture',     'Step back in time inside the ancient amphitheater of Rome.',             '3 hours',   50.0, 'Rome',  '09:30 AM'),
    ('Rome City Walking Tour',        'Sightseeing', 'Discover Trevi Fountain, Pantheon, and Piazza Navona with a guide.',    '2 hours',   20.0, 'Rome',  '04:00 PM'),
    ('Trastevere Evening Food Tour',  'Experience',  'Sample traditional Roman pasta, gelato, and Italian wines.',             '3 hours',   65.0, 'Rome',  '06:30 PM'),
    ('Sensoji Temple Walking Tour',   'Culture',     "Tokyo's oldest ancient Buddhist temple and historic Nakamise street.",   '2 hours',   15.0, 'Tokyo', '10:00 AM'),
    ('Tokyo Street Food Crawl',       'Experience',  'Yakitori, ramen, and matcha desserts in vibrant Shinjuku.',              '3 hours',   55.0, 'Tokyo', '05:30 PM'),
    ('Sagrada Familia Fast-Track',    'Culture',     "Gaudí's unfinished cathedral masterpiece in Barcelona.",                 '2 hours',   38.0, 'Barcelona', '11:00 AM'),
    ('Park Güell & Mosaic Walk',      'Nature',      'Colorful mosaic park with sweeping city and sea views by Gaudí.',        '2 hours',   14.0, 'Barcelona', '03:00 PM'),
    ('Tower of London & Crown Jewels','Sightseeing', 'Historic castle on the Thames housing royal treasures.',                '2.5 hours', 32.0, 'London', '10:00 AM'),
    ('British Museum Highlights',     'Culture',     'World-famous museum covering 2 million years of human history.',         '3 hours',    0.0, 'London', '01:30 PM'),
    ('Burj Khalifa At The Top',       'Sightseeing', "Observation deck on the world's tallest building at 555m.",             '1.5 hours', 45.0, 'Dubai',  '05:00 PM'),
    ('Dubai Desert Safari & BBQ',     'Adventure',   'Dune bashing, camel riding, falconry, and starlit BBQ dinner.',          '6 hours',   70.0, 'Dubai',  '03:00 PM')
]


def seed_activities():
    """Seed sample activities if table is empty."""
    db    = get_db()
    count = db.execute('SELECT COUNT(*) FROM activities').fetchone()[0]
    if count == 0:
        db.executemany(
            'INSERT INTO activities (name, category, description, duration, cost, city, preferred_time) VALUES (?,?,?,?,?,?,?)',
            SAMPLE_ACTIVITIES
        )
        db.commit()
    db.close()


# ── GET /api/activities  — List all activities ────────────────
@activities_bp.route('/activities', methods=['GET'])
def get_activities():
    """List activities with optional city, category, and query filters."""
    seed_activities()
    city = request.args.get('city', '').strip()
    q    = request.args.get('q',    '').strip()
    cat  = request.args.get('category', '').strip()

    sql    = 'SELECT * FROM activities WHERE 1=1'
    params = []

    if city:
        sql += ' AND LOWER(city) LIKE ?'
        params.append(f'%{city.lower()}%')
    if q:
        sql += ' AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)'
        params.append(f'%{q.lower()}%')
        params.append(f'%{q.lower()}%')
    if cat:
        sql += ' AND category = ?'
        params.append(cat)

    sql += ' ORDER BY city, name'

    db   = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return jsonify({'success': True, 'data': [dict(r) for r in rows]})


# ── POST /api/activities  — Create new activity ───────────────
@activities_bp.route('/activities', methods=['POST'])
def create_activity():
    """Create a new activity (Name, Description, Category, Duration, Cost, City/Stop, Preferred Time)."""
    d    = request.get_json() or {}
    name = (d.get('name') or '').strip()

    if not name:
        return jsonify({'success': False, 'message': 'Activity name is required'}), 400

    category       = (d.get('category') or 'Sightseeing').strip()
    description    = (d.get('description') or '').strip()
    duration       = (d.get('duration') or '1 hour').strip()
    cost           = float(d.get('cost') or 0)
    city           = (d.get('city') or '').strip()
    preferred_time = (d.get('preferred_time') or d.get('time') or '').strip()

    db = get_db()
    cursor = db.execute(
        '''INSERT INTO activities (name, category, description, duration, cost, city, preferred_time)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (name, category, description, duration, cost, city, preferred_time)
    )
    activity_id = cursor.lastrowid
    db.commit()

    activity = db.execute('SELECT * FROM activities WHERE id = ?', (activity_id,)).fetchone()
    db.close()

    return jsonify({'success': True, 'message': 'Activity created successfully!', 'data': dict(activity)}), 201


# ── POST /api/trips/<trip_id>/activities  — Add activity to trip/stop ──
@activities_bp.route('/trips/<int:trip_id>/activities', methods=['POST'])
def add_activity_to_trip(trip_id):
    """Add an activity to a specific trip and auto-associate with matching city stop if available."""
    d           = request.get_json() or {}
    activity_id = d.get('activity_id')
    stop_id     = d.get('stop_id')
    day_number  = d.get('day_number', 1)
    act_time    = d.get('activity_time') or d.get('time', '')
    notes       = d.get('notes', '')

    if not activity_id:
        return jsonify({'success': False, 'message': 'activity_id is required'}), 400

    db = get_db()
    activity = db.execute('SELECT * FROM activities WHERE id = ?', (activity_id,)).fetchone()
    if not activity:
        db.close()
        return jsonify({'success': False, 'message': 'Activity not found'}), 404

    # If stop_id was not provided, check if trip has a stop for this activity's city
    if not stop_id and activity['city']:
        match_stop = db.execute(
            'SELECT id FROM trip_stops WHERE trip_id = ? AND LOWER(city) = LOWER(?) ORDER BY stop_order ASC LIMIT 1',
            (trip_id, activity['city'])
        ).fetchone()
        if match_stop:
            stop_id = match_stop['id']

    cursor = db.execute(
        '''INSERT INTO trip_activities (trip_id, activity_id, stop_id, day_number, activity_time, notes)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (trip_id, activity_id, stop_id, day_number, act_time, notes)
    )
    link_id = cursor.lastrowid
    db.commit()

    # Retrieve stop city if stop_id is set
    stop_city = activity['city']
    if stop_id:
        srow = db.execute('SELECT city FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
        if srow:
            stop_city = srow['city']

    db.close()

    return jsonify({
        'success': True,
        'message': f'"{activity["name"]}" added to {stop_city}!',
        'data': {
            'id': link_id,
            'trip_id': trip_id,
            'activity_id': activity_id,
            'stop_id': stop_id,
            'day_number': day_number,
            'activity_time': act_time,
            'name': activity['name'],
            'city': stop_city
        }
    }), 201


# ── POST /api/activities/<aid>/add  — Legacy add route compatibility ──
@activities_bp.route('/activities/<int:aid>/add', methods=['POST'])
def add_to_trip_legacy(aid):
    """Legacy route to add activity to trip."""
    d       = request.get_json() or {}
    trip_id = d.get('trip_id', 1)
    day_num = d.get('day_number', 1)
    stop_id = d.get('stop_id')
    notes   = d.get('notes', '')

    db = get_db()
    activity = db.execute('SELECT * FROM activities WHERE id=?', (aid,)).fetchone()
    if not activity:
        db.close()
        return jsonify({'success': False, 'message': 'Activity not found'}), 404

    if not stop_id and activity['city']:
        match_stop = db.execute(
            'SELECT id FROM trip_stops WHERE trip_id = ? AND LOWER(city) = LOWER(?) LIMIT 1',
            (trip_id, activity['city'])
        ).fetchone()
        if match_stop:
            stop_id = match_stop['id']

    db.execute(
        'INSERT INTO trip_activities (trip_id, activity_id, stop_id, day_number, notes) VALUES (?,?,?,?,?)',
        (trip_id, aid, stop_id, day_num, notes)
    )
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': f'"{activity["name"]}" added to your trip!'})


# ── DELETE /api/trips/<trip_id>/activities/<activity_id> ──
@activities_bp.route('/trips/<int:trip_id>/activities/<int:activity_id>', methods=['DELETE'])
def remove_activity_from_trip(trip_id, activity_id):
    """Remove an activity association from a trip."""
    db = get_db()
    db.execute(
        'DELETE FROM trip_activities WHERE trip_id = ? AND activity_id = ?',
        (trip_id, activity_id)
    )
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Activity removed from trip.'})


# ── DELETE /api/trip-activities/<int:link_id> ──
@activities_bp.route('/trip-activities/<int:link_id>', methods=['DELETE'])
def delete_trip_activity_by_id(link_id):
    """Remove a specific trip_activities link by ID."""
    db = get_db()
    db.execute('DELETE FROM trip_activities WHERE id = ?', (link_id,))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Trip activity removed.'})
