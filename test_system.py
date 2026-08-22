import urllib.request
import json

base = 'http://localhost:5000/api'


def req(method, path, body=None):
    url = base + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'} if data else {}
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r).read())


def main():
    print('=== GLOBETROTTER FULL SYSTEM INTEGRATION TEST ===', flush=True)

    # Step 1: Health
    h = req('GET', '/health')
    print('1. Health check OK:', h['success'], flush=True)
    assert h['success'] is True

    # Step 2: Trip Creation
    t = req('POST', '/trips', {
        'name': 'Grand European Tour 2026',
        'description': 'Paris, Rome & Barcelona multi-city expedition',
        'start_date': '2026-09-15',
        'end_date': '2026-09-20',
        'is_public': 0,
        'stops': [{'city': 'Paris'}, {'city': 'Rome'}]
    })
    trip_id = t['data']['id']
    print(f'2. Trip created ID: {trip_id} - "{t["data"]["title"]}"', flush=True)
    assert trip_id > 0

    # Step 3: Add 3rd destination stop
    stop3 = req('POST', f'/trips/{trip_id}/stops', {'city': 'Barcelona', 'country': 'Spain'})
    print('3. Added destination stop:', stop3['message'], flush=True)

    # Step 4: Activities Discovery & Assignment
    acts = req('GET', '/activities')['data']
    eiffel  = next(a for a in acts if 'Eiffel' in a['name'])
    colo    = next(a for a in acts if 'Colosseum' in a['name'])
    sagrada = next(a for a in acts if 'Sagrada' in a['name'])

    l1 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': eiffel['id']})
    l2 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': colo['id']})
    l3 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': sagrada['id']})
    print('4. Linked 3 activities to destinations successfully', flush=True)

    # Step 5: Activity Scheduling (Itinerary Engine)
    link_id = l1['data'].get('id') or l1['data'].get('trip_activity_id')
    sched = req('PUT', f'/trip-activities/{link_id}/schedule', {
        'activity_date': '2026-09-15',
        'activity_time': '10:00 AM',
        'notes': 'Fast-track priority entry tickets booked'
    })
    print('5. Rescheduled activity:', sched['message'], flush=True)

    # Step 6: Fetch Day-Wise Itinerary
    itin = req('GET', f'/trips/{trip_id}/itinerary')['data']
    total_acts = len(itin.get('chronological', []))
    print('6. Itinerary engine total days:', len(itin.get('itinerary', [])), '| Total items:', total_acts, flush=True)
    assert total_acts >= 3

    # Step 7: Budget Engine Calculation
    budget = req('GET', f'/trips/{trip_id}/budget')['data']
    print(f'7. Budget Engine -> Total: ${budget["total_cost"]} | Daily Avg: ${budget["avg_cost_per_day"]}/day', flush=True)
    assert budget['total_cost'] > 0

    # Step 8: Public Sharing Toggle & Read-Only View
    share = req('POST', f'/trips/{trip_id}/share')['data']
    print('8. Public Sharing URL generated:', share['public_url'], flush=True)
    assert share['is_public'] == 1

    pub_view = req('GET', f'/trips/public/{trip_id}')['data']
    print('   Public Payload Title:', pub_view['trip']['title'], '| Stops:', len(pub_view['trip']['stops']), flush=True)
    assert pub_view['trip']['title'] == 'Grand European Tour 2026'

    print('\n[SUCCESS] ALL 8 INTEGRATION STEPS PASSED 100% PERFECTLY!', flush=True)


if __name__ == '__main__':
    main()
