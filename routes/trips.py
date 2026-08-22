from flask import Blueprint, request, jsonify
from database import get_db

trips_bp = Blueprint('trips', __name__)


# ── GET /api/trips  —  list all trips (optionally filter by user) ──
@trips_bp.route('/trips', methods=['GET'])
def get_trips():
    user_id = request.args.get('user_id')
    db      = get_db()

    if user_id:
        rows = db.execute(
            'SELECT * FROM trips WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()
    else:
        rows = db.execute(
            'SELECT * FROM trips ORDER BY created_at DESC'
        ).fetchall()

    db.close()
    return jsonify({'success': True, 'data': [dict(r) for r in rows]})


# ── POST /api/trips  —  create a new trip ─────────────────────────
@trips_bp.route('/trips', methods=['POST'])
def create_trip():
    d = request.get_json() or {}

    # Validate required fields
    if not d.get('title'):
        return jsonify({'success': False, 'message': 'Trip name is required'}), 400

    user_id     = d.get('user_id',     1)
    title       = d.get('title',       '').strip()
    description = d.get('description', '').strip()
    start_date  = d.get('start_date',  '')
    end_date    = d.get('end_date',    '')
    is_public   = 1 if d.get('is_public') else 0

    db = get_db()
    cursor = db.execute(
        '''INSERT INTO trips (user_id, title, description, start_date, end_date, is_public)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, title, description, start_date, end_date, is_public)
    )
    trip_id = cursor.lastrowid
    db.commit()

    # Return the created trip
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()
    db.close()

    return jsonify({'success': True, 'message': 'Trip created!', 'data': dict(trip)}), 201


# ── GET /api/trips/<id>  —  get a single trip with its activities ─
@trips_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    db   = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    # Also fetch activities linked to this trip
    activities = db.execute(
        '''SELECT a.*, ta.day_number, ta.notes
           FROM activities a
           JOIN trip_activities ta ON a.id = ta.activity_id
           WHERE ta.trip_id = ?
           ORDER BY ta.day_number, a.name''',
        (trip_id,)
    ).fetchall()

    db.close()
    result = dict(trip)
    result['activities'] = [dict(a) for a in activities]
    return jsonify({'success': True, 'data': result})


# ── PUT /api/trips/<id>  —  update a trip ─────────────────────────
@trips_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    db   = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    d           = request.get_json() or {}
    title       = d.get('title',       trip['title'])
    description = d.get('description', trip['description'])
    start_date  = d.get('start_date',  trip['start_date'])
    end_date    = d.get('end_date',    trip['end_date'])
    is_public   = d.get('is_public',   trip['is_public'])

    db.execute(
        '''UPDATE trips
           SET title=?, description=?, start_date=?, end_date=?, is_public=?
           WHERE id=?''',
        (title, description, start_date, end_date, is_public, trip_id)
    )
    db.commit()
    updated = db.execute('SELECT * FROM trips WHERE id=?', (trip_id,)).fetchone()
    db.close()

    return jsonify({'success': True, 'message': 'Trip updated!', 'data': dict(updated)})


# ── DELETE /api/trips/<id>  —  delete a trip ──────────────────────
@trips_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    db   = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    # Remove linked activities first (maintain referential integrity)
    db.execute('DELETE FROM trip_activities WHERE trip_id = ?', (trip_id,))
    db.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': 'Trip deleted!'})
