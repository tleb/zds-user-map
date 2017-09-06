class RefreshToken:
    key = 'refresh_token'

    def __init__(self, store):
        self.store = store

    def set(self, value):
        self.store[self.key] = value

    def get(self):
        return self.store[self.key]
