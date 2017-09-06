import requests


class ZesteDeSavoir:

    uris = {
        'base': 'https://zestedesavoir.com',
        'user': '/api/membres/{}/',
        'token': '/oauth2/token/',
        'send': '/api/mps/{}/messages/',
        'topics': '/api/mps/?page={}',
        'unread_topics': '/api/mps/unread/?page={}',
        'msgs': '/api/mps/{}/messages/?page={}',
    }

    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None

    def get_user(self, user_id):
        return self._request(self.uris['user'].format(user_id))

    def send_message(self, topic_id, msg):
        res = self._request(self.uris['send'].format(topic_id), 'POST', {'text': msg}, False, False)

        # if it's a 403, it's most likely that it's because we can't write in
        # the topic because we are alone
        if res.status_code != 403:
            res.raise_for_status()

        return res.json()

    def topics(self, unread, page=1):
        res = self._request(self.uris['unread_topics' if unread else 'topics'].format(page))

        yield from res['results']

        if res['next']:
            yield from self.topics(unread, page+1)

    def last_message_not_from_bot(self, topic_id, bot_id, page=1, last_message=None):
        res = self._request(self.uris['msgs'].format(topic_id, page))

        # if we find a message on this page, it's the new last_message not
        # from bot
        if len(res['results']):
            try:
                last_message = next(msg for msg in reversed(res['results']) if msg['author'] != bot_id)
            except StopIteration:
                pass

        if not res['next']:
            return last_message

        return self.last_message_not_from_bot(topic_id, bot_id, page+1, last_message)

    def _request(self, uri, method='GET', body=None, json=True, raise_error=True):
        if self.access_token is None:
            self._refresh_tokens()

        print(method + ' ' + uri)
        res = requests.request(
            method,
            self.uris['base'] + uri,
            headers={'Authorization': 'Bearer ' + self.access_token},
            json=body)

        if res.status_code == 401:
            self.access_token = None
            return self._request(uri, method, body)

        if raise_error:
            res.raise_for_status()

        return res.json() if json else res

    def _refresh_tokens(self):
        print('refreshing tokens')
        res = requests.post(self.uris['base'] + self.uris['token'], json={
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token.get(),
        }).json()

        self.access_token = res['access_token']
        self.refresh_token.set(res['refresh_token'])

        print('refreshed tokens')
