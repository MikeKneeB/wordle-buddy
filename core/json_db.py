import json
import os

from core.wutils import *


class JsonWordleDB:

    def __init__(self, root_dir):
        self._root_dir = root_dir

    def save(self, guild, name, result):
        os.makedirs(os.path.join(self._root_dir, str(guild), str(name)), exist_ok=True)
        with open(os.path.join(self._root_dir, str(guild), str(name),
                               f'{result["week_number"]}.json'),
                  'w') as result_file:
            result_file.write(json.dumps(result))

    def load(self, guild, names=None, weeks=None):
        if not names:
            names = self._get_all_names(guild)
        if not weeks:
            weeks = [current_day()]
        result = {}
        for name in names:
            result[name] = []
            for week in weeks:
                result[name] += [self._load_one(guild, name, week)]
        return result

    def _load_one(self, guild, name, week):
        try:
            with open(os.path.join(self._root_dir, str(guild), str(name), f'{week}.json'),
                      'r') as result_file:
                return json.load(result_file)
        except FileNotFoundError:
            return None

    def _get_all_names(self, guild):
        try:
            return [int(i) for i in os.listdir(os.path.join(self._root_dir, str(guild)))]
        except FileNotFoundError:
            return []
