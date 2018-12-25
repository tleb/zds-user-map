import json
import requests
import urllib.parse
from collections import OrderedDict
from zeste_de_savoir import ZesteDeSavoir


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

def marker_from_topic(topic, zds, config, osm_ti):
    msgs = list(zds.messages(topic['id']))
    msgs.reverse()

    pos, user_id = None, None

    for msg in msgs:
        if msg['author'] == config['bot_id']:
            continue

        if msg['text'] == config['deletion_msg']:
            break

        osm_ti.start()
        pos = get_pos(msg['text'])
        if pos is not None:
            user_id = msg['author']
            break

    if pos is None:
        return None

    user = zds.get_user(user_id)
    return OrderedDict([
        ('id', user_id),
        ('username', user['username']),
        ('url', ZesteDeSavoir.URI_BASE + user['html_url']),
        ('lat', pos['lat']),
        ('lon', pos['lon'])])
