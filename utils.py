import json
import requests
import urllib.parse
from collections import OrderedDict
from zeste_de_savoir import ZesteDeSavoir
import subprocess


OSM_SEARCH = 'http://nominatim.openstreetmap.org/search?format=json&q={}'


def new_marker(id, username, url, lat, lon):
    return OrderedDict([
        ('id', id),
        ('username', username),
        ('url', url),
        ('lat', lat),
        ('lon', lon)])


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
        if msg['author'] in config['blacklist']:
            return None
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
    return new_marker(
        user_id,
        user['username'],
        ZesteDeSavoir.URI_BASE + user['html_url'],
        pos['lat'],
        pos['lon'])


# returns (bool, str or None)
# first is true if markers has been changed
# second is an optional message to send
def on_new_message(msg, config, markers, zds, osm_ti):
    if msg['author'] in config['blacklist']:
        return (False, None)
    if msg['author'] == config['bot_id']:
        return (False, None)

    # delete the marker
    if msg['text'] == config['deletion_msg']:
        try:
            del markers[msg['author']]
            return (True, config['answerDeletion'])
        except KeyError:
            return (False, config['answerDeletion'])

    osm_ti.start()
    pos = get_pos(msg['text'])
    if pos is None:
        return (False, config['answerNotFound'])

    user_id = msg['author']
    user = zds.get_user(user_id)

    markers[user_id] = new_marker(
        user_id,
        user['username'],
        ZesteDeSavoir.URI_BASE + user['html_url'],
        pos['lat'],
        pos['lon'])

    return (True, config['answerFound'].format(pos['display_name'], pos['lat'], pos['lon']))


def retrieve_markers(path):
    try:
        with open(path, 'r', encoding='UTF-8') as f:
            return [new_marker(**m) for m in json.load(f)]
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []


def save_markers(path, markers):
    data = list(markers.values())
    data.sort(key=lambda m: m['id'])

    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=2)


def git_send_markers(markers_path):
    print('git add {}'.format(markers_path))
    subprocess.call(['git', 'add', markers_path])
    print('git commit -m "[bot] save markers"')
    subprocess.call(['git', 'commit', '-m', '[bot] save markers'])
    print('git push origin master')
    subprocess.call(['git', 'push', 'origin', 'master'])
