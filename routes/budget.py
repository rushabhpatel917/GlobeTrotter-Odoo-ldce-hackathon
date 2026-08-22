from flask import Blueprint, request, jsonify
from database import get_db
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

VALID_CATEGORIES = ['Transport', 'Stay', 'Activities', 'Meals', 'Other']


def calculate_trip_budget(db, trip_id):
    """
    Reusable Budget Calculation Engine:
    - Calculates category totals for Transport, Stay, Activities, Meals, Other
    - Calculates activity costs dynamically from scheduled itinerary
    - Calculates total trip cost
    - Calculates average cost per day based on trip duration
    """
    trip = db.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip:
        return None

    # 1. Calculate duration in days
    duration_days = 1
    if trip['start_date'] and trip['end_date']:
        try:
            d1 = datetime.strptime(trip['start_date'], '%Y-%m-%d').date()
            d2 = datetime.strptime(trip['end_date'], '%Y-%m-%d').date()
            diff = (d2 - d1).days + 1
            if diff > 0:
                duration_days = diff
        except Exception:
            duration_days = 1

    # 2. Initialize category totals
    cat_totals = {
        'Transport': 0.0,
        'Stay': 0.0,
        'Activities': 0.0,
        'Meals': 0.0,
        'Other': 0.0
    }

    # 3. Calculate Activities total dynamically from itinerary
    activities_rows = db.execute(
        '''SELECT ta.id as trip_activity_id, a.id as activity_id, a.name, a.cost, a.category, a.city,
                  ta.activity_date, ta.activity_time, ta.notes
           FROM trip_activities ta
           JOIN activities a ON ta.activity_id = a.id
           WHERE ta.trip_id = ?''',
        (trip_id,)
    ).fetchall()

    activities_list = []
    activities_sum  = 0.0
    for r in activities_rows:
        cost = float(r['cost'] or 0)
        activities_sum += cost
        activities_list.append({
            'trip_activity_id': r['trip_activity_id'],
            'activity_id': r['activity_id'],
            'name': r['name'],
            'category': r['category'],
            'city': r['city'],
            'cost': cost,
            'date': r['activity_date'],
            'time': r['activity_time'],
            'notes': r['notes']
        })

    cat_totals['Activities'] = activities_sum

    # 4. Calculate custom expenses totals (Transport, Stay, Meals, Other)
    expenses_rows = db.execute(
        '''SELECT id, category, title, cost, notes, created_at
           FROM trip_expenses
           WHERE trip_id = ?
           ORDER BY created_at DESC''',
        (trip_id,)
    ).fetchall()

    expenses_list = []
    for e in expenses_rows:
        cat  = e['category'] if e['category'] in cat_totals else 'Other'
        cost = float(e['cost'] or 0)
        if cat != 'Activities':
            cat_totals[cat] += cost
        expenses_list.append({
            'id': e['id'],
            'category': cat,
            'title': e['title'],
            'cost': cost,
            'notes': e['notes'],
            'created_at': e['created_at']
        })

    # 5. Total trip cost & Average per day
    total_cost = sum(cat_totals.values())
    avg_cost_per_day = round(total_cost / duration_days, 2)

    # 6. Format category breakdown with percentages
    category_breakdown = {}
    for c_name, c_cost in cat_totals.items():
        pct = round((c_cost / total_cost * 100), 1) if total_cost > 0 else 0.0
        category_breakdown[c_name] = {
            'cost': round(c_cost, 2),
            'percentage': pct
        }

    return {
        'trip_id': trip['id'],
        'trip_title': trip['title'],
        'start_date': trip['start_date'],
        'end_date': trip['end_date'],
        'duration_days': duration_days,
        'total_cost': round(total_cost, 2),
        'avg_cost_per_day': avg_cost_per_day,
        'categories': category_breakdown,
        'category_totals': {k: round(v, 2) for k, v in cat_totals.items()},
        'custom_expenses': expenses_list,
        'activities_breakdown': activities_list
    }


# ── GET /api/trips/<trip_id>/budget — Retrieve full budget calculation ──
@budget_bp.route('/trips/<int:trip_id>/budget', methods=['GET'])
def get_trip_budget(trip_id):
    """Retrieve reliable trip budget calculations with category breakdown and per-day average."""
    db = get_db()
    data = calculate_trip_budget(db, trip_id)
    db.close()

    if not data:
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    return jsonify({'success': True, 'data': data})


# ── POST /api/trips/<trip_id>/expenses — Add custom expense item ───────
@budget_bp.route('/trips/<int:trip_id>/expenses', methods=['POST'])
def add_trip_expense(trip_id):
    """Add a custom expense item (Transport, Stay, Meals, Other)."""
    d        = request.get_json() or {}
    category = (d.get('category') or 'Other').strip()
    title    = (d.get('title') or '').strip()
    cost     = float(d.get('cost') or 0)
    notes    = (d.get('notes') or '').strip()

    if not title:
        return jsonify({'success': False, 'message': 'Expense title is required'}), 400

    if category not in VALID_CATEGORIES or category == 'Activities':
        category = 'Other'

    db = get_db()
    trip = db.execute('SELECT id FROM trips WHERE id = ?', (trip_id,)).fetchone()
    if not trip:
        db.close()
        return jsonify({'success': False, 'message': 'Trip not found'}), 404

    cursor = db.execute(
        '''INSERT INTO trip_expenses (trip_id, category, title, cost, notes)
           VALUES (?, ?, ?, ?, ?)''',
        (trip_id, category, title, cost, notes)
    )
    expense_id = cursor.lastrowid
    db.commit()

    updated_budget = calculate_trip_budget(db, trip_id)
    db.close()

    return jsonify({
        'success': True,
        'message': f'Added expense "{title}" (${cost:.2f})',
        'data': {
            'expense_id': expense_id,
            'budget': updated_budget
        }
    }), 201


# ── DELETE /api/trips/expenses/<expense_id> — Remove custom expense ──
@budget_bp.route('/trips/expenses/<int:expense_id>', methods=['DELETE'])
def delete_trip_expense(expense_id):
    """Delete a custom expense item."""
    db = get_db()
    expense = db.execute('SELECT * FROM trip_expenses WHERE id = ?', (expense_id,)).fetchone()
    if not expense:
        db.close()
        return jsonify({'success': False, 'message': 'Expense not found'}), 404

    trip_id = expense['trip_id']
    db.execute('DELETE FROM trip_expenses WHERE id = ?', (expense_id,))
    db.commit()

    updated_budget = calculate_trip_budget(db, trip_id)
    db.close()

    return jsonify({
        'success': True,
        'message': 'Expense removed successfully.',
        'data': {
            'budget': updated_budget
        }
    })
