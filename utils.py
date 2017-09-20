import json
import requests
import urllib.parse


OSM_SEARCH = 'http://nominatim.openstreetmap.org/search?format=json&q={}'


def get_pos(query):
    res = requests.get(
        OSM_SEARCH.format(urllib.parse.quote(query)))
    if res.status_code != 200:
        return None

    data = res.json()
    return data[0] if data else None


def list_markers(store, base_uri):
    for user_id, latlng in store.loop():
        if user_id.startswith('user.'):
            # len('user.') == 5
            user_id = user_id[5:]
            user = store['userData.' + user_id]

            yield {
                'username': user['username'],
                'uri': base_uri + user['uri'],
                'latlng': latlng,
            }


def save_markers(path, markers):
    markers.sort(key=lambda x: x['username'].lower())
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(markers, f, indent=2, sort_keys=True)
