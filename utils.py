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


def last_text_position(msgs, bot_id, deletion_msg):
        last_position = None

        for msg in msgs:
            if msg['author'] == bot_id:
                continue

            if msg['text'] == deletion_msg:
                last_position = None

            last_position = msg['text']

        return last_position
