class Context(object):
    def __init__(self):
        self._values = {}

    def set(self, key, value):
        self._values[key] = value

    def get(self, key):
       return self._values[key]