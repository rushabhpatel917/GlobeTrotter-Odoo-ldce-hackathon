from flask import Blueprint, request, jsonify
from database import get_db

trips_bp = Blueprint('trips', __name__)


# ── GET /api/trips  —  list all trips ──────────────────────────────
@trips_bp.route('/trips', methods=['GET'])
def get_trips():
    """Fetch all trips or filter by user_id/owner."""
    user_id = request.args.get('user_id') or request.args.get('owner_id')
    db      = get_db()

    if user_id:
        rows = db.execute(
            '''SELECT t.*, u.name as owner_name, u.email as owner_email 
               FROM trips t 
               LEFT JOIN users u ON t.user_id = u.id 
               WHERE t.user_id = ? 
               ORDER BY t.created_at DESC''',
            (user_id,)
        ).fetchall()
    else:
        rows = db.execute(
            '''SELECT t.*, u.name as owner_name, u.email as owner_email 
               FROM trips t 
               LEFT JOIN users u ON t.user_id = u.id 
               ORDER BY t.created_at DESC'''
        ).fetchall()

    trips_list = [dict(r) for r in rows]

    # Attach stop summary if available
    for trip in trips_list:
        stops = db.execute(
            'SELECT city, country, stop_order FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC',
            (trip['id'],)
        ).fetchall()
        trip['stops_summary'] = [f"{s['city']}{', ' + s['country'] if s['country'] else ''}" for s in stops]

    db.close()
    return jsonify({'success': True, 'data': trips_list})


# ── POST /api/trips  —  create a new trip ─────────────────────────
@trips_bp.route('/trips', methods=['POST'])
def create_trip():
    """Create a new trip supporting title/name, description, dates, owner, and optional initial stops."""
    d = request.get_json() or {}

    title = (d.get('title') or d.get('name') or '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Trip name/title is required'}), 400

    user_id     = d.get('user_id') or d.get('owner_id') or 1
    description = (d.get('description') or '').strip()
    start_date  = (d.get('start_date') or '').strip()
    end_date    = (d.get('end_date') or '').strip()
    is_public   = 1 if d.get('is_public') else 0

    if start_date and end_date and end_date < start_date:
        return jsonify({'success': False, 'message': 'End date cannot be before start date'}), 400

    db = get_db()
    cursor = db.execute(
        '''INSERT INTO trips (user_id, title, description, start_date, end_date, is_public)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, title, description, start_date, end_date, is_public)
    )
    trip_id = cursor.lastrowid

    # If initial stops are provided as an array
    initial_stops = d.get('stops', [])
    if isinstance(initial_stops, list):
        for idx, stop in enumerate(initial_stops, start=1):
            city = stop.get('city', '').strip()
            if city:
                db.execute(
                    '''INSERT INTO trip_stops (trip_id, city, country, start_date, end_date, stop_order)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (trip_id, city, stop.get('country', ''), stop.get('start_date', ''), stop.get('end_date', ''), stop.get('stop_order', idx))
                )

    db.commit()

    trip = db.execute(
        '''SELECT t.*, u.name as owner_name 
           FROM trips t 
           LEFT JOIN users u ON t.user_id = u.id 
           WHERE t.id = ?''', 
        (trip_id,)
    ).fetchone()

    stops = db.execute('SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC', (trip_id,)).fetchall()
    db.close()

    result = dict(trip)
    result['stops'] = [dict(s) for s in stops]

    return jsonify({'success': True, 'message': 'Trip created successfully!', 'data': result}), 201


# ── GET /api/trips/<id>  —  get trip with stops and activities ─────
@trips_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Retrieve trip details along with multi-city stops and scheduled activities."""
    db   = get_db()
    trip = db.execute(
        '''SELECT t.*, u.name as owner_name, u.email as owner_email 
           FROM trips t 
           LEFT JOIN users u ON t.user_id = u.id 
           WHERE t.id = ?''', 
        (trip_id,)
    ).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    # Fetch multi-city stops ordered by stop_order
    stops = db.execute(
        'SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC',
        (trip_id,)
    ).fetchall()

    # Fetch linked activities
    activities = db.execute(
        '''SELECT a.*, ta.day_number, ta.notes, ta.id as trip_activity_id
           FROM activities a
           JOIN trip_activities ta ON a.id = ta.activity_id
           WHERE ta.trip_id = ?
           ORDER BY ta.day_number, a.name''',
        (trip_id,)
    ).fetchall()

    db.close()
    result = dict(trip)
    result['stops'] = [dict(s) for s in stops]
    result['activities'] = [dict(a) for a in activities]
    return jsonify({'success': True, 'data': result})


# ── PUT /api/trips/<id>  —  update a trip ─────────────────────────
@trips_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    """Update trip attributes."""
    db   = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    d           = request.get_json() or {}
    title       = (d.get('title') or d.get('name') or trip['title']).strip()
    description = d.get('description', trip['description'])
    start_date  = d.get('start_date',  trip['start_date'])
    end_date    = d.get('end_date',    trip['end_date'])
    is_public   = d.get('is_public',   trip['is_public'])
    user_id     = d.get('user_id') or d.get('owner_id') or trip['user_id']

    if start_date and end_date and end_date < start_date:
        db.close()
        return jsonify({'success': False, 'message': 'End date cannot be before start date'}), 400

    db.execute(
        '''UPDATE trips
           SET title=?, description=?, start_date=?, end_date=?, is_public=?, user_id=?
           WHERE id=?''',
        (title, description, start_date, end_date, is_public, user_id, trip_id)
    )
    db.commit()
    updated = db.execute(
        '''SELECT t.*, u.name as owner_name 
           FROM trips t 
           LEFT JOIN users u ON t.user_id = u.id 
           WHERE t.id=?''', 
        (trip_id,)
    ).fetchone()
    db.close()

    return jsonify({'success': True, 'message': 'Trip updated successfully!', 'data': dict(updated)})


# ── DELETE /api/trips/<id>  —  delete a trip ──────────────────────
@trips_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    """Delete a trip and cascade delete its linked stops and activities."""
    db   = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    db.execute('DELETE FROM trip_stops WHERE trip_id = ?', (trip_id,))
    db.execute('DELETE FROM trip_activities WHERE trip_id = ?', (trip_id,))
    db.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': 'Trip deleted successfully!'})


# ── TRIP STOPS ENDPOINTS (Multi-City Support) ─────────────────────

# GET /api/trips/<trip_id>/stops
@trips_bp.route('/trips/<int:trip_id>/stops', methods=['GET'])
def get_trip_stops(trip_id):
    """Fetch all stops for a specific trip ordered by stop_order."""
    db = get_db()
    stops = db.execute(
        'SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC',
        (trip_id,)
    ).fetchall()
    db.close()
    return jsonify({'success': True, 'data': [dict(s) for s in stops]})


# POST /api/trips/<trip_id>/stops
@trips_bp.route('/trips/<int:trip_id>/stops', methods=['POST'])
def add_trip_stop(trip_id):
    """Add a new stop (City, Country, Dates, Order) to a trip."""
    d    = request.get_json() or {}
    city = (d.get('city') or '').strip()

    if not city:
        return jsonify({'success': False, 'message': 'City name is required'}), 400

    country    = (d.get('country') or '').strip()
    start_date = (d.get('start_date') or '').strip()
    end_date   = (d.get('end_date') or '').strip()

    db = get_db()
    # Check if trip exists
    trip = db.execute('SELECT id FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    # Calculate stop_order if not provided
    stop_order = d.get('stop_order')
    if stop_order is None:
        max_order = db.execute('SELECT MAX(stop_order) FROM trip_stops WHERE trip_id = ?', (trip_id,)).fetchone()[0]
        stop_order = (max_order or 0) + 1

    cursor = db.execute(
        '''INSERT INTO trip_stops (trip_id, city, country, start_date, end_date, stop_order)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (trip_id, city, country, start_date, end_date, stop_order)
    )
    stop_id = cursor.lastrowid
    db.commit()

    new_stop = db.execute('SELECT * FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
    db.close()

    return jsonify({'success': True, 'message': f'Added stop: {city}', 'data': dict(new_stop)}), 201


# DELETE /api/trips/stops/<stop_id>
@trips_bp.route('/trips/stops/<int:stop_id>', methods=['DELETE'])
def delete_trip_stop(stop_id):
    """Remove a stop from a trip."""
    db = get_db()
    stop = db.execute('SELECT * FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
    if not stop:
        db.close()
        return jsonify({'success': False, 'message': 'Stop not found'}), 404

    db.execute('DELETE FROM trip_stops WHERE id = ?', (stop_id,))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': f'Removed stop: {stop["city"]}'})
