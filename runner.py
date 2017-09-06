from store import Store
from zeste_de_savoir import ZesteDeSavoir
from refresh_token import RefreshToken
import yaml
import utils
import subprocess
import time


class Runner:
    def __init__(self, config_path, store_path, data_path):
        self.config = self._load_config(config_path)
        self.store = Store(store_path)
        self.zds = ZesteDeSavoir(
            self.config['client_id'],
            self.config['client_secret'],
            RefreshToken(self.store)
        )
        self.data_path = data_path

    def _load_config(self, path):
        with open(path, encoding='UTF-8') as f:
            return yaml.load(f)

    def run(self):
        self.run_once()

        if not self.config['init']:
            time.sleep(self.config['interval'])
            self.run()

    def run_once(self):
        print('started running')

        for topic in self.zds.topics(not self.config['init']):
            msg = self.zds.last_message_not_from_bot(topic['id'], self.config['bot_id'])
            self._on_new_message(topic['id'], msg['text'], msg['author'])

        markers = utils.list_markers(self.store, self.zds.uris['base'])
        utils.save_markers(self.data_path, list(markers))

        subprocess.call(['git', 'add', self.data_path])
        subprocess.call(['git', 'commit', '-m', '[bot] save data'])
        subprocess.call(['git', 'push', 'origin', 'master'])

        print('pushed')

    def _on_new_message(self, topic_id, msg_text, msg_author):
        if msg_author in self.config['blacklist']:
            return

        pos = utils.get_pos(msg_text)

        if pos:
            answer = self.config['answerFound'].format(pos['display_name'], pos['lat'], pos['lon'])
        else:
            answer = self.config['answerNotFound']

        self.zds.send_message(topic_id, answer)
        print('answer sent')

        if pos:
            self._record(msg_author, [pos['lat'], pos['lon']])

    def _record(self, user_id, latlng):
        self.store['user.{}'.format(user_id)] = latlng

        if 'userData.{}'.format(user_id) not in self.store:
            user = self.zds.get_user(user_id)
            self.store['userData.{}'.format(user_id)] = {
                'uri': user['html_url'],
                'username': user['username']
            }
