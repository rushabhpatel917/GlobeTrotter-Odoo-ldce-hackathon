from flask import Blueprint, request, jsonify
from database import get_db

activities_bp = Blueprint('activities', __name__)

# ── Sample data seeded on first load ──────────────────────────
SAMPLE_ACTIVITIES = [
    ('Eiffel Tower Visit',    'Sightseeing', 'Iconic iron lattice tower on the Champ de Mars in Paris',       '3 hours',   25.0, 'Paris'),
    ('Louvre Museum',         'Culture',     "World's largest art museum and home to the Mona Lisa",           '4 hours',   17.0, 'Paris'),
    ('Seine River Cruise',    'Experience',  'Scenic boat cruise along the Seine river past major landmarks',  '1.5 hours', 15.0, 'Paris'),
    ('Montmartre Walk',       'Culture',     'Explore the artistic hilltop neighbourhood and Sacré-Cœur',     '2 hours',    0.0, 'Paris'),
    ('Colosseum Tour',        'Sightseeing', 'Ancient amphitheatre at the heart of Rome — gladiators fought here', '2 hours', 16.0, 'Rome'),
    ('Vatican Museums',       'Culture',     'Breathtaking museums housing Sistine Chapel & Renaissance art', '3 hours',   20.0, 'Rome'),
    ('Trevi Fountain',        'Sightseeing', 'Baroque masterpiece — toss a coin and make a wish!',            '1 hour',     0.0, 'Rome'),
    ('Sagrada Familia',       'Culture',     "Gaudi's unfinished basilica — a UNESCO World Heritage Site",    '2 hours',   26.0, 'Barcelona'),
    ('Park Güell',            'Nature',      'Colorful mosaic park with sweeping city views by Gaudi',        '2 hours',   10.0, 'Barcelona'),
    ('La Boqueria Market',    'Experience',  'Famous public market bursting with fresh food and local flavors','1 hour',     0.0, 'Barcelona'),
    ('Big Ben & Westminster', 'Sightseeing', 'Iconic clock tower standing beside the Houses of Parliament',   '1 hour',     0.0, 'London'),
    ('British Museum',        'Culture',     'Free world-famous museum covering 2 million years of history', '3 hours',    0.0, 'London'),
    ('Tower of London',       'Sightseeing', 'Historic castle on the Thames housing the Crown Jewels',        '2 hours',   30.0, 'London'),
    ('Tokyo Tower',           'Sightseeing', 'Communications and observation tower inspired by Eiffel Tower', '2 hours',   12.0, 'Tokyo'),
    ('Senso-ji Temple',       'Culture',     "Tokyo's oldest Buddhist temple in the Asakusa district",        '1.5 hours',  0.0, 'Tokyo'),
    ('Shibuya Crossing',      'Experience',  'World-famous scramble crossing — busiest pedestrian crossing',  '30 mins',    0.0, 'Tokyo'),
    ('Taj Mahal',             'Sightseeing', 'Ivory-white marble mausoleum on the banks of the Yamuna river','3 hours',   15.0, 'Agra'),
    ('Dubai Desert Safari',   'Adventure',   'Off-road dune bashing followed by camel ride and BBQ dinner',  '6 hours',   60.0, 'Dubai'),
    ('Burj Khalifa Deck',     'Sightseeing', "Observation deck on the world's tallest building at 555m",     '1.5 hours', 35.0, 'Dubai'),
    ('Santorini Sunset',      'Experience',  'Watch the legendary sunset from Oia village over the caldera', '2 hours',    0.0, 'Santorini'),
]


def seed_activities():
    """Seed sample activities if the table is empty."""
    db    = get_db()
    count = db.execute('SELECT COUNT(*) FROM activities').fetchone()[0]
    if count == 0:
        db.executemany(
            'INSERT INTO activities (name, category, description, duration, cost, city) VALUES (?,?,?,?,?,?)',
            SAMPLE_ACTIVITIES
        )
        db.commit()
    db.close()


# ── GET /api/activities ────────────────────────────────────────
@activities_bp.route('/activities', methods=['GET'])
def get_activities():
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
        sql += ' AND LOWER(name) LIKE ?'
        params.append(f'%{q.lower()}%')
    if cat:
        sql += ' AND category = ?'
        params.append(cat)

    sql += ' ORDER BY city, name'

    db   = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return jsonify({'success': True, 'data': [dict(r) for r in rows]})


# ── POST /api/activities/<id>/add ─────────────────────────────
@activities_bp.route('/activities/<int:aid>/add', methods=['POST'])
def add_to_trip(aid):
    d       = request.get_json() or {}
    trip_id = d.get('trip_id',    1)
    day_num = d.get('day_number', 1)

    db = get_db()
    # Verify activity exists
    activity = db.execute('SELECT * FROM activities WHERE id=?', (aid,)).fetchone()
    if not activity:
        db.close()
        return jsonify({'success': False, 'message': 'Activity not found'}), 404

    db.execute(
        'INSERT INTO trip_activities (trip_id, activity_id, day_number) VALUES (?,?,?)',
        (trip_id, aid, day_num)
    )
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': f'"{activity["name"]}" added to your trip!'})
