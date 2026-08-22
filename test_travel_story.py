import urllib.request
import json
import sys

base = 'http://localhost:5000/api'


def req(method, path, body=None):
    url = base + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'} if data else {}
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(r).read())


def main():
    print('=== GLOBETROTTER TRAVEL PLANNING QA STORY TEST ===', flush=True)

    # 1. Create a multi-city trip
    trip_res = req('POST', '/trips', {
        'name': 'Paris & Rome Grand Vacation',
        'description': 'A 2-day dual city cultural and food tour across France and Italy.',
        'start_date': '2026-09-01',
        'end_date': '2026-09-02',
        'is_public': 0,
        'stops': [
            {'city': 'Paris', 'country': 'France', 'start_date': '2026-09-01', 'end_date': '2026-09-01'},
            {'city': 'Rome', 'country': 'Italy', 'start_date': '2026-09-02', 'end_date': '2026-09-02'}
        ]
    })
    assert trip_res['success'] is True
    trip_id = trip_res['data']['id']
    print(f'1. Multi-City Trip Created -> ID {trip_id}: "{trip_res["data"]["title"]}"', flush=True)

    # 2. Fetch destination stops
    stops = req('GET', f'/trips/{trip_id}/stops')['data']
    print(f'2. Verified {len(stops)} Destination Stops: {[s["city"] for s in stops]}', flush=True)
    assert len(stops) == 2
    paris_stop = next(s for s in stops if s['city'] == 'Paris')
    rome_stop  = next(s for s in stops if s['city'] == 'Rome')

    # 3. Add activities to each destination
    acts = req('GET', '/activities')['data']
    print('   Available Activities in DB:', [a['name'] for a in acts], flush=True)

    paris_acts = [a for a in acts if 'Paris' in a.get('city', '') or 'Eiffel' in a['name'] or 'Louvre' in a['name']]
    rome_acts  = [a for a in acts if 'Rome' in a.get('city', '') or 'Colosseum' in a['name']]

    eiffel = paris_acts[0]
    louvre = paris_acts[1] if len(paris_acts) > 1 else acts[1]
    colo   = rome_acts[0] if len(rome_acts) > 0 else acts[2]
    rome2  = rome_acts[1] if len(rome_acts) > 1 else acts[3]

    a1 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': eiffel['id'], 'stop_id': paris_stop['id']})['data']
    a2 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': louvre['id'], 'stop_id': paris_stop['id']})['data']
    a3 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': colo['id'], 'stop_id': rome_stop['id']})['data']
    a4 = req('POST', f'/trips/{trip_id}/activities', {'activity_id': rome2['id'], 'stop_id': rome_stop['id']})['data']
    print('3. Added 4 Activities across Paris and Rome stops successfully.', flush=True)

    # 4. Assign activities to specific days & times
    req('PUT', f'/trip-activities/{a1["id"]}/schedule', {'activity_date': '2026-09-01', 'activity_time': '09:00 AM'})
    req('PUT', f'/trip-activities/{a2["id"]}/schedule', {'activity_date': '2026-09-01', 'activity_time': '02:00 PM'})
    req('PUT', f'/trip-activities/{a3["id"]}/schedule', {'activity_date': '2026-09-02', 'activity_time': '10:00 AM'})
    req('PUT', f'/trip-activities/{a4["id"]}/schedule', {'activity_date': '2026-09-02', 'activity_time': '04:00 PM'})
    print('4. Assigned Activities to Day 1 (Paris) and Day 2 (Rome).', flush=True)

    # 5. Verify itinerary ordering
    itin = req('GET', f'/trips/{trip_id}/itinerary')['data']
    days = itin['itinerary']
    print(f'5. Verified Chronological Itinerary -> Days Count: {len(days)}', flush=True)

    day1_cities = days[0]['cities']
    print(f'   Day 1 ({days[0]["date"]}): City = {day1_cities[0]["city"]}, Activities = {[a["name"] for a in day1_cities[0]["activities"]]}', flush=True)
    assert day1_cities[0]['city'] == 'Paris'
    assert len(day1_cities[0]['activities']) == 2

    day2_cities = days[1]['cities']
    print(f'   Day 2 ({days[1]["date"]}): City = {day2_cities[0]["city"]}, Activities = {[a["name"] for a in day2_cities[0]["activities"]]}', flush=True)
    assert day2_cities[0]['city'] == 'Rome'
    assert len(day2_cities[0]['activities']) == 2

    # 6. Verify activity costs calculation
    budget = req('GET', f'/trips/{trip_id}/budget')['data']
    expected_total = eiffel['cost'] + louvre['cost'] + colo['cost'] + rome2['cost']
    print(f'6. Verified Activity Cost Calculation -> Calculated: ${budget["total_cost"]} | Expected: ${expected_total}', flush=True)
    assert budget['total_cost'] == expected_total

    # 7. Verify trip summary
    pub = req('GET', f'/trips/public/{trip_id}')['data']
    print(f'7. Verified Executive Trip Summary -> Title: "{pub["trip"]["title"]}", Total Stops: {len(pub["trip"]["stops"])}', flush=True)
    assert pub['trip']['title'] == 'Paris & Rome Grand Vacation'
    assert len(pub['trip']['stops']) == 2

    print('\n[SUCCESS] TRAVEL PLANNING QA STORY TEST COMPLETED 100% PERFECTLY!', flush=True)


if __name__ == '__main__':
    main()
