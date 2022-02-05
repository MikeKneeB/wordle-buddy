import json

import pytest
import os

from wordle_buddy import json_db as jdb
from unittest.mock import patch
from unittest.mock import mock_open

TEST_ROOT_PATH = 'root'


normal_inputs = (
    1029,
    10512,
    {
        'week_number': 321,
        'score': 3,
        'matrix': [[0, 0, 0, 0, 0],
                   [0, 1, 0, 2, 0],
                   [2, 2, 2, 2, 2]]
    }
)


@pytest.mark.parametrize(
    'guild,name,result',
    [
        pytest.param(*normal_inputs, id='Test normal save')
    ]
)
def test_save(guild, name, result):
    m = mock_open()
    with patch('wordle_buddy.json_db.open', m),\
            patch(f'platform.system') as mock_system:
        mock_system.return_value = 'linux'
        test_db = jdb.JsonWordleDB(TEST_ROOT_PATH)
        test_db.save(guild, name, result)
    m.assert_called_once_with(os.path.join(TEST_ROOT_PATH, str(guild), str(name), f'{result["week_number"]}.json'), 'w')
    handle = m()
    handle.write.assert_called_once_with(json.dumps(result))
