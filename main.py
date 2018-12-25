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
        TimeInterval(1.2))

    osm_ti = TimeInterval(1.2)

    if mode == 0:
        zds._refresh_token_from_logins(input('Username: '), getpass())

    if mode == 1:
        topics = list(zds.topics(False))
        topics.reverse()

        markers = [utils.marker_from_topic(topic, zds, config, osm_ti)
                    for topic in topics]
        markers = [x for x in markers if x is not None]
        markers.sort(key=lambda m: m['id'])

        with open(MARKERS_PATH, 'w', encoding='UTF-8') as f:
            json.dump(markers, f, indent=2)

    if mode == 2:
        pass



if __name__ == '__main__':
    main(int(sys.argv[1]) if 1 < len(sys.argv) and sys.argv[1].isdigit() else -1)
