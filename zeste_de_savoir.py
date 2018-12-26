import requests


class ZesteDeSavoir:

    URI_BASE = 'https://zestedesavoir.com'
    URI_USER = '/api/membres/{}/'
    URI_TOKEN = '/oauth2/token/'
    URI_SEND = '/api/mps/{}/messages/'
    URI_TOPICS = '/api/mps/?page={}'
    URI_UNREAD_TOPICS = '/api/mps/unread/?page={}'
    URI_MSGS = '/api/mps/{}/messages/?page={}'

    def __init__(self, client_id, client_secret, refresh_token_path, time_interval):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token_path = refresh_token_path
        self._refresh_token = self._retrieve_refresh_token()
        self.access_token = None
        self.time_interval = time_interval

    def get_user(self, user_id):
        return self._request(self.URI_USER.format(user_id))

    def send_message(self, topic_id, msg):
        res = self._request(self.URI_SEND.format(topic_id),
                            'POST', {'text': msg}, False, False)

        # if it's a 403, it's most likely that it's because we can't write in
        # the topic because we are alone
        if res.status_code != 403:
            res.raise_for_status()

        return res.json()

    def topics(self, unread, page=1):
        uri = self.URI_UNREAD_TOPICS if unread else self.URI_TOPICS
        res = self._request(uri.format(page))

        yield from res['results']

        if res['next']:
            yield from self.topics(unread, page+1)

    def messages(self, topic_id, page=1):
        res = self._request(self.URI_MSGS.format(topic_id, page))

        yield from res['results']

        if res['next']:
            yield from self.messages(topic_id, page+1)

    def _request(self, uri, method='GET', body=None, json=True, raise_error=True):
        if self.access_token is None:
            self._refresh_tokens()

        self.time_interval.start()
        print(method + ' ' + uri)
        res = requests.request(
            method,
            self.URI_BASE + uri,
            headers={'Authorization': 'Bearer ' + self.access_token},
            json=body)

        if res.status_code == 401:
            self.access_token = None
            return self._request(uri, method, body)

        if raise_error:
            res.raise_for_status()

        return res.json() if json else res

    def _refresh_tokens(self):
        if self._refresh_token is None:
            raise RuntimeError(
                'missing refresh token, please use mode 0 to initialise it')

        self.time_interval.start()
        print('POST {}'.format(self.URI_TOKEN))
        res = requests.post(self.URI_BASE + self.URI_TOKEN, json={
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self._refresh_token,
        }).json()

        self.access_token = res['access_token']

        self._refresh_token = res['refresh_token']
        self._save_refresh_token()

    def _refresh_token_from_logins(self, username, password):
        self.time_interval.start()
        print('POST {}'.format(self.URI_TOKEN))
        res = requests.post(self.URI_BASE + self.URI_TOKEN, json={
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': username,
            'password': password,
        }).json()

        self._refresh_token = res['refresh_token']
        self._save_refresh_token()

    def _retrieve_refresh_token(self):
        try:
            with open(self.refresh_token_path, 'r', encoding='UTF-8') as f:
                res = f.readline().strip()
                return res if res != '' else None
        except FileNotFoundError:
            return None

    def _save_refresh_token(self):
        with open(self.refresh_token_path, 'w', encoding='UTF-8') as f:
            f.write(self._refresh_token)
