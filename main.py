from zeste_de_savoir import ZesteDeSavoir
from time_interval import TimeInterval
import utils

from getpass import getpass
import sys
import yaml
import subprocess
import time
import json
from collections import OrderedDict


CONFIG_PATH = 'config.yml'
REFRESH_TOKEN_PATH = 'refresh_token.txt'
MARKERS_PATH = 'docs/markers.json'


def main(mode):
    if not (0 <= mode <= 2):
        return print('''Available modes:
0: initialise the refresh token based on the username and password
1: initialise the data (add every marker)
2: daemon mode (watch new topics)''')

    with open(CONFIG_PATH, encoding='UTF-8') as f:
        config = yaml.load(f)

    zds = ZesteDeSavoir(
        config['client_id'],
        config['client_secret'],
        REFRESH_TOKEN_PATH,
        TimeInterval(0))

    osm_ti = TimeInterval(0)

    if mode == 0:
        zds._refresh_token_from_logins(input('Username: '), getpass())

    if mode == 1:
        topics = list(zds.topics(False))
        # start from the oldest topic
        topics.reverse()

        markers = [utils.marker_from_topic(topic, zds, config, osm_ti)
                    for topic in topics]

        # ignore None and only keep the latest marker for each id
        markers = {m['id']: m for m in markers if m is not None}

        utils.save_markers(MARKERS_PATH, markers)

    if mode == 2:
        topics = list(zds.topics(True))
        topics.reverse()

        markers = {m['id']: m for m in utils.retrieve_markers(MARKERS_PATH)}

        while True:
            has_changed = False
            topics = list(zds.topics(True))
            topics.reverse()

            for topic in topics:
                msg = list(zds.messages(topic['id']))[-1]

                if msg['author'] in config['blacklist']:
                    continue
                if msg['author'] == config['bot_id']:
                    continue

                # delete the marker
                if msg['text'] == config['deletion_msg']:
                    has_changed = True
                    del markers[msg['author']]
                    zds.send_message(topic['id'], config['answerDeletion'])
                    continue

                osm_ti.start()
                pos = utils.get_pos(msg['text'])
                if pos is None:
                    zds.send_message(topic['id'], config['answerNotFound'])
                else:
                    has_changed = True
                    user_id = msg['author']
                    user = zds.get_user(user_id)

                    markers[user_id] = utils.new_marker(
                        user_id,
                        user['username'],
                        ZesteDeSavoir.URI_BASE + user['html_url'],
                        pos['lat'],
                        pos['lon'])

                    zds.send_message(
                        topic['id'],
                        config['answerFound'].format(pos['display_name'], pos['lat'], pos['lon']))

            if has_changed:
                utils.save_markers(MARKERS_PATH, markers)

            time.sleep(config['interval'])



if __name__ == '__main__':
    main(int(sys.argv[1]) if 1 < len(sys.argv) and sys.argv[1].isdigit() else -1)
