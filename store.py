import json


class Store:
    def __init__(self, path):
        self.path = path
        self.data = self._read()

    def __setitem__(self, key, value):
        self.data[key] = value
        self._save(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def _read(self):
        try:
            with open(self.path, 'r', encoding='UTF-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return {}

    def _save(self, data):
        with open(self.path, 'w', encoding='UTF-8') as f:
            return json.dump(data, f, indent=2)

    def __contains__(self, key):
        return key in self.data

    def delete(self, key):
        if isinstance(key, str):
            del self.data[k]
        else:
            for k in key:
                del self.data[k]

        self._save(self.data)

    def loop(self):
        yield from self.data.items()
