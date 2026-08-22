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


# ── GET /api/trips/<id>  —  get trip with stops and assigned activities ─────
@trips_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Retrieve trip details along with multi-city stops and activities assigned to each stop."""
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
    raw_stops = db.execute(
        'SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC',
        (trip_id,)
    ).fetchall()
    stops = [dict(s) for s in raw_stops]

    # Fetch linked activities with stop details
    raw_activities = db.execute(
        '''SELECT a.*, ta.day_number, ta.notes, ta.stop_id, ta.activity_time, ta.id as trip_activity_id,
                  s.city as stop_city, s.country as stop_country
           FROM trip_activities ta
           JOIN activities a ON ta.activity_id = a.id
           LEFT JOIN trip_stops s ON ta.stop_id = s.id
           WHERE ta.trip_id = ?
           ORDER BY ta.stop_id, ta.day_number, a.name''',
        (trip_id,)
    ).fetchall()
    activities = [dict(a) for a in raw_activities]

    # Attach activities array to each stop (Trip -> Stop -> Activities)
    for stop in stops:
        stop['activities'] = [
            a for a in activities 
            if a.get('stop_id') == stop['id'] or (not a.get('stop_id') and a.get('city', '').lower() == stop['city'].lower())
        ]

    db.close()
    result = dict(trip)
    result['stops'] = stops
    result['activities'] = activities
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


# ── PUBLIC SHARING ENDPOINTS (M4 Turn 5) ──────────────────────────────────

@trips_bp.route('/trips/<int:trip_id>/share', methods=['POST'])
def share_trip(trip_id):
    """Toggle a trip to public status and generate shareable public link."""
    db = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    db.execute('UPDATE trips SET is_public = 1 WHERE id = ?', (trip_id,))
    db.commit()
    db.close()

    public_url = f'/static/public-trip.html?id={trip_id}'
    return jsonify({
        'success': True,
        'message': 'Trip is now public and shareable!',
        'data': {
            'trip_id': trip_id,
            'is_public': 1,
            'public_url': public_url
        }
    })


@trips_bp.route('/trips/public/<int:trip_id>', methods=['GET'])
def get_public_trip(trip_id):
    """Fetch complete public read-only trip payload including stops, activities, itinerary, and budget."""
    db = get_db()
    trip = db.execute(
        '''SELECT t.*, u.name as owner_name 
           FROM trips t 
           LEFT JOIN users u ON t.user_id = u.id 
           WHERE t.id = ?''',
        (trip_id,)
    ).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Public trip not found'}), 404

    trip_dict = dict(trip)

    # Fetch stops and assigned activities
    stops = db.execute(
        'SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC',
        (trip_id,)
    ).fetchall()
    stops_list = [dict(s) for s in stops]

    for s in stops_list:
        acts = db.execute(
            '''SELECT a.*, ta.id as trip_activity_id, ta.activity_date, ta.activity_time, ta.notes
               FROM trip_activities ta
               JOIN activities a ON ta.activity_id = a.id
               WHERE ta.stop_id = ? OR (ta.trip_id = ? AND LOWER(a.city) = LOWER(?))''',
            (s['id'], trip_id, s['city'])
        ).fetchall()
        s['activities'] = [dict(a) for a in acts]

    trip_dict['stops'] = stops_list

    # Calculate budget summary for public view
    from routes.budget import calculate_trip_budget
    budget_data = calculate_trip_budget(db, trip_id)

    db.close()

    return jsonify({
        'success': True,
        'data': {
            'trip': trip_dict,
            'budget': budget_data
        }
    })


# ── TRIP STOPS ENDPOINTS (Multi-City & Activity Association) ─────────────────────

# GET /api/trips/<trip_id>/stops
@trips_bp.route('/trips/<int:trip_id>/stops', methods=['GET'])
def get_trip_stops(trip_id):
    """Fetch all stops for a specific trip ordered by stop_order with activities."""
    db = get_db()
    raw_stops = db.execute(
        'SELECT * FROM trip_stops WHERE trip_id = ? ORDER BY stop_order ASC',
        (trip_id,)
    ).fetchall()
    stops = [dict(s) for s in raw_stops]

    for stop in stops:
        acts = db.execute(
            '''SELECT a.*, ta.id as trip_activity_id, ta.day_number, ta.activity_time, ta.notes
               FROM trip_activities ta
               JOIN activities a ON ta.activity_id = a.id
               WHERE ta.stop_id = ? OR (ta.trip_id = ? AND LOWER(a.city) = LOWER(?))''',
            (stop['id'], trip_id, stop['city'])
        ).fetchall()
        stop['activities'] = [dict(a) for a in acts]

    db.close()
    return jsonify({'success': True, 'data': stops})


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
    trip = db.execute('SELECT id FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

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


# POST /api/trips/stops/<stop_id>/activities  — Add activity to a specific City Stop
@trips_bp.route('/trips/stops/<int:stop_id>/activities', methods=['POST'])
def add_activity_to_stop(stop_id):
    """Add an activity to a specific city stop."""
    d           = request.get_json() or {}
    activity_id = d.get('activity_id')
    day_number  = d.get('day_number', 1)
    act_time    = d.get('activity_time') or d.get('time', '')
    notes       = d.get('notes', '')

    if not activity_id:
        return jsonify({'success': False, 'message': 'activity_id is required'}), 400

    db   = get_db()
    stop = db.execute('SELECT * FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
    if not stop:
        db.close()
        return jsonify({'success': False, 'message': 'City stop not found'}), 404

    activity = db.execute('SELECT * FROM activities WHERE id = ?', (activity_id,)).fetchone()
    if not activity:
        db.close()
        return jsonify({'success': False, 'message': 'Activity not found'}), 404

    cursor = db.execute(
        '''INSERT INTO trip_activities (trip_id, activity_id, stop_id, day_number, activity_time, notes)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (stop['trip_id'], activity_id, stop_id, day_number, act_time, notes)
    )
    link_id = cursor.lastrowid
    db.commit()
    db.close()

    return jsonify({
        'success': True,
        'message': f'Added "{activity["name"]}" to {stop["city"]}',
        'data': {
            'id': link_id,
            'trip_id': stop['trip_id'],
            'stop_id': stop_id,
            'activity_id': activity_id,
            'name': activity['name'],
            'city': stop['city']
        }
    }), 201


# DELETE /api/trips/stops/<stop_id>/activities/<activity_id>  — Remove activity from a City Stop
@trips_bp.route('/trips/stops/<int:stop_id>/activities/<int:activity_id>', methods=['DELETE'])
def remove_activity_from_stop(stop_id, activity_id):
    """Remove an activity from a specific city stop."""
    db = get_db()
    db.execute('DELETE FROM trip_activities WHERE stop_id = ? AND activity_id = ?', (stop_id, activity_id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Activity removed from stop.'})


# PUT /api/trips/stops/<stop_id>  — Edit Stop or Reorder
@trips_bp.route('/trips/stops/<int:stop_id>', methods=['PUT'])
def update_trip_stop(stop_id):
    """Update stop details (city, country, start_date, end_date, stop_order)."""
    db   = get_db()
    stop = db.execute('SELECT * FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
    if not stop:
        db.close()
        return jsonify({'success': False, 'message': 'Stop not found'}), 404

    d          = request.get_json() or {}
    city       = (d.get('city') or stop['city']).strip()
    country    = d.get('country', stop['country'])
    start_date = d.get('start_date', stop['start_date'])
    end_date   = d.get('end_date', stop['end_date'])
    stop_order = d.get('stop_order', stop['stop_order'])

    db.execute(
        '''UPDATE trip_stops
           SET city=?, country=?, start_date=?, end_date=?, stop_order=?
           WHERE id=?''',
        (city, country, start_date, end_date, stop_order, stop_id)
    )
    db.commit()
    updated = db.execute('SELECT * FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
    db.close()

    return jsonify({'success': True, 'message': f'Updated stop: {city}', 'data': dict(updated)})


# DELETE /api/trips/stops/<stop_id>
@trips_bp.route('/trips/stops/<int:stop_id>', methods=['DELETE'])
def delete_trip_stop(stop_id):
    """Remove a stop from a trip."""
    db = get_db()
    stop = db.execute('SELECT * FROM trip_stops WHERE id = ?', (stop_id,)).fetchone()
    if not stop:
        db.close()
        return jsonify({'success': False, 'message': 'Stop not found'}), 404

    db.execute('DELETE FROM trip_activities WHERE stop_id = ?', (stop_id,))
    db.execute('DELETE FROM trip_stops WHERE id = ?', (stop_id,))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': f'Removed stop: {stop["city"]}'})
