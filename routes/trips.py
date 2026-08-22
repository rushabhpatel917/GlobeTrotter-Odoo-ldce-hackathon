from flask import Blueprint, request, jsonify
from database import get_db

trips_bp = Blueprint('trips', __name__)


# ── GET /api/trips  —  list all trips (optionally filter by user/owner) ──
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

    db.close()
    return jsonify({'success': True, 'data': [dict(r) for r in rows]})


# ── POST /api/trips  —  create a new trip with validation ─────────
@trips_bp.route('/trips', methods=['POST'])
def create_trip():
    """Create a new trip supporting title/name, description, start_date, end_date, user_id/owner."""
    d = request.get_json() or {}

    # Support both 'title' and 'name' keys
    title = (d.get('title') or d.get('name') or '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Trip name/title is required'}), 400

    user_id     = d.get('user_id') or d.get('owner_id') or 1
    description = (d.get('description') or '').strip()
    start_date  = (d.get('start_date') or '').strip()
    end_date    = (d.get('end_date') or '').strip()
    is_public   = 1 if d.get('is_public') else 0

    # Date range validation
    if start_date and end_date and end_date < start_date:
        return jsonify({'success': False, 'message': 'End date cannot be before start date'}), 400

    db = get_db()
    cursor = db.execute(
        '''INSERT INTO trips (user_id, title, description, start_date, end_date, is_public)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, title, description, start_date, end_date, is_public)
    )
    trip_id = cursor.lastrowid
    db.commit()

    # Retrieve the inserted trip record
    trip = db.execute(
        '''SELECT t.*, u.name as owner_name 
           FROM trips t 
           LEFT JOIN users u ON t.user_id = u.id 
           WHERE t.id = ?''', 
        (trip_id,)
    ).fetchone()
    db.close()

    return jsonify({'success': True, 'message': 'Trip created successfully!', 'data': dict(trip)}), 201


# ── GET /api/trips/<id>  —  get single trip details with activities ─
@trips_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Retrieve trip details along with all scheduled activities."""
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
    result['activities'] = [dict(a) for a in activities]
    return jsonify({'success': True, 'data': result})


# ── PUT /api/trips/<id>  —  update an existing trip ─────────────────
@trips_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    """Update trip attributes (title, description, start_date, end_date, owner)."""
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

    # Date range validation if updating dates
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
    """Delete a trip and cascade delete its linked activities."""
    db   = get_db()
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()

    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    # Remove linked activities first
    db.execute('DELETE FROM trip_activities WHERE trip_id = ?', (trip_id,))
    db.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': 'Trip deleted successfully!'})
