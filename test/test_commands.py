import datetime
import discord
import pytest

from wordle_buddy import commands as wc
from unittest.mock import patch
from unittest.mock import call


TEST_DATE = datetime.datetime(day=27, month=1, year=2021)
TEST_DATE_BEFORE = datetime.datetime(day=26, month=1, year=2021)
TEST_DAY_NUM = 321


normal_inputs = (4, {'Mike': 7, 'Melissa': 5})
normal_ldb = '''```Wordle Leaderboard: 23/01/2021 - 26/01/2021
===========================================
POS NAME           SCORE
-------------------------------------------
1   Mike           7
2   Melissa        5```'''
empty_inputs = (1, {})
empty_ldb = '''```Wordle Leaderboard: 26/01/2021 - 26/01/2021
===========================================
POS NAME           SCORE
-------------------------------------------```'''


@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(normal_inputs, normal_ldb, id="Normal input produces leaderboard"),
        pytest.param(empty_inputs, empty_ldb, id="Empty input produces header only")
    ]
)
def test_ldb_message(test_input, test_output):
    with patch(f'{wc.__name__}.datetime', wraps=datetime) as mock_dt:
        mock_dt.datetime.today.return_value = TEST_DATE
        assert wc._ldb_message(*test_input) == test_output


normal_ave_inputs = (4, {'Mike': (3.333333, 3), 'Melissa': (5, 2)})
normal_ave_ldb = '''```Wordle Average Leaderboard: 23/01/2021 - 26/01/2021
===========================================
POS NAME           SCORE  TOTAL GAMES
-------------------------------------------
1   Mike           3.333  3
2   Melissa        5.000  2```'''
empty_ave_inputs = (1, {})
empty_ave_ldb = '''```Wordle Average Leaderboard: 26/01/2021 - 26/01/2021
===========================================
POS NAME           SCORE  TOTAL GAMES
-------------------------------------------```'''


@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(normal_ave_inputs, normal_ave_ldb, id="Normal average input produces leaderboard"),
        pytest.param(empty_ave_inputs, empty_ave_ldb, id="Empty average input produces header only")
    ]
)
def test_ave_ldb_message(test_input, test_output):
    with patch(f'{wc.__name__}.datetime', wraps=datetime) as mock_dt:
        mock_dt.datetime.today.return_value = TEST_DATE
        assert wc._ave_ldb_message(*test_input) == test_output


normal_results = [{'score': 3}, {'score': 5}]
normal_output = 8
none_results = [None, None]
none_output = 14
empty_results = []
empty_output = 0


@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(normal_results, normal_output, id="Results are added correctly"),
        pytest.param(none_results, none_output, id="None results are treated as 7"),
        pytest.param(empty_results, empty_output, id="Empty results return 0")
    ]
)
def test_total_score(test_input, test_output):
    assert wc._total_score(test_input) == test_output


normal_ave_output = 4.0, 2
none_mixed_results = [{'score': 3}, None, {'score': 5}]
zero_output = 0, 0


@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(normal_results, normal_ave_output, id="Results are averaged correctly"),
        pytest.param(none_results, zero_output, id="None results are not counted"),
        pytest.param(none_mixed_results, normal_ave_output, id="None results are not counted"),
        pytest.param(empty_results, zero_output, id="Empty results return 0")
    ]
)
def test_ave_score(test_input, test_output):
    assert wc._ave_score(test_input) == test_output

@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(
            '',
            (wc.WordleCommandHandler.Response.NONE, None),
            id='Empty message returns NONE'),
        pytest.param(
            'w+ solve',
            (wc.WordleCommandHandler.Response.NONE, None),
            id='Invalid command message returns NONE'),
        pytest.param(
            'w+',
            (wc.WordleCommandHandler.Response.NONE, None),
            id='Command message without command returns NONE'),
        pytest.param(
            'This is an unrelated message',
            (wc.WordleCommandHandler.Response.NONE, None),
            id='Unrelated message returns NONE')
    ]
)
async def test_handle_general(test_input, test_output):
    with patch('discord.Guild') as MockGuild, \
            patch('discord.Message') as MockMessage:
        guild_inst = MockGuild.return_value
        message = MockMessage.return_value
        message.content = test_input
        handler = wc.WordleCommandHandler(None)
        assert await handler.handle_command(guild_inst, message) == test_output


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(
            '+w help',
            (wc.WordleCommandHandler.Response.MSG_PRIVATE, 'Hi!'),
            id='Help command is called for a help request'),
    ]
)
async def test_handle_help(test_input, test_output):
    with patch('discord.Guild') as MockGuild,\
            patch('discord.Message') as MockMessage,\
            patch.object(wc.WordleCommandHandler, '_help') as mock_help:
        guild_inst = MockGuild.return_value
        message = MockMessage.return_value
        message.content = test_input
        mock_help.return_value = test_output
        handler = wc.WordleCommandHandler(None)
        assert await handler.handle_command(guild_inst, message) == test_output
        mock_help.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(
            '+w leaderboard',
            (wc.WordleCommandHandler.Response.MSG_CHANNEL, 'My cool leaderboard'),
            id='Leaderboard command is called for a leaderboard request'),
        pytest.param(
            '+w leaderboard extra args',
            (wc.WordleCommandHandler.Response.MSG_CHANNEL, 'My cool leaderboard'),
            id='Leaderboard command with additional arguments is called for a leaderboard request'),
    ]
)
async def test_handle_leaderboard(test_input, test_output):
    with patch('discord.Guild') as MockGuild, \
            patch('discord.Message') as MockMessage, \
            patch.object(wc.WordleCommandHandler, '_leaderboard') as mock_leaderboard:
        guild_inst = MockGuild.return_value
        message = MockMessage.return_value
        message.content = test_input
        mock_leaderboard.return_value = test_output
        handler = wc.WordleCommandHandler(None)
        assert await handler.handle_command(guild_inst, message) == test_output
        mock_leaderboard.assert_called_once_with(guild_inst, test_input.split()[2:])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(
            '+w average',
            (wc.WordleCommandHandler.Response.MSG_CHANNEL, 'My cool leaderboard'),
            id='Average command is called'),
        pytest.param(
            '+w average extra args',
            (wc.WordleCommandHandler.Response.MSG_CHANNEL, 'My cool leaderboard'),
            id='Average command is called with additional arguments')
    ]
)
async def test_handle_average(test_input, test_output):
    with patch('discord.Guild') as MockGuild, \
            patch('discord.Message') as MockMessage, \
            patch.object(wc.WordleCommandHandler, '_average_ldb') as mock_average_ldb:
        guild_inst = MockGuild.return_value
        message = MockMessage.return_value
        message.content = test_input
        mock_average_ldb.return_value = test_output
        handler = wc.WordleCommandHandler(None)
        assert await handler.handle_command(guild_inst, message) == test_output
        mock_average_ldb.assert_called_once_with(guild_inst, test_input.split()[2:])


class DummyMem:
    def __init__(self, name):
        self.display_name = name


normal_raw_results = {1029: [
        {
            'week_number': TEST_DAY_NUM,
            'score': 3,
            'matrix': [[0, 0, 0, 0, 0],
                       [0, 1, 0, 2, 0],
                       [2, 2, 2, 2, 2]]
        }
    ]
}
normal_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
                      '''```Wordle Leaderboard: 24/01/2021 - 26/01/2021
===========================================
POS NAME           SCORE
-------------------------------------------
1   1029           3```''')
month_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
                     '''```Wordle Leaderboard: 31/12/2020 - 26/01/2021
===========================================
POS NAME           SCORE
-------------------------------------------
1   1029           3```''')
five_day_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
                        '''```Wordle Leaderboard: 22/01/2021 - 26/01/2021
===========================================
POS NAME           SCORE
-------------------------------------------
1   1029           3```''')
invalid_test_output = (wc.WordleCommandHandler.Response.NONE, None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'additional,calls_db,days,raw_results,test_output',
    [
        pytest.param(None, True, TEST_DATE.isoweekday(), normal_raw_results, normal_test_output,
                     id='No additional commands'),
        pytest.param([], True, TEST_DATE.isoweekday(), normal_raw_results, normal_test_output,
                     id='Empty additional commands'),
        pytest.param(['week'], True, TEST_DATE.isoweekday(), normal_raw_results, normal_test_output,
                     id='Week leaderboard request'),
        pytest.param(['month'], True, TEST_DATE.day, normal_raw_results, month_test_output,
                     id='Month leaderboard request'),
        pytest.param(['5'], True, 5, normal_raw_results, five_day_test_output, id='Days leaderboard request'),
        pytest.param(['invalid'], False, 0, None, invalid_test_output, id='Invalid leaderboard request')
    ]
)
async def test_leaderboard(additional, calls_db, days, raw_results, test_output):
    with patch.object(discord.Guild, 'fetch_member') as mock_fetch_member, \
            patch('wordle_buddy.json_db.JsonWordleDB') as MockDB, \
            patch('wordle_buddy.utils.current_day') as mock_current_day, \
            patch(f'{wc.__name__}.datetime', wraps=datetime) as mock_dt:
        guild_inst = discord.Guild
        guild_inst.id = 99
        mock_db = MockDB.return_value
        if calls_db:
            mock_fetch_member.side_effect = [DummyMem(str(k)) for k in raw_results.keys()]
            mock_db.load.return_value = raw_results
        mock_current_day.return_value = TEST_DAY_NUM
        mock_dt.datetime.today.return_value = TEST_DATE
        handler = wc.WordleCommandHandler(mock_db)
        assert await handler._leaderboard(guild_inst, additional) == test_output
        if calls_db:
            mock_db.load.assert_called_once_with(99, weeks=range(TEST_DAY_NUM - days, TEST_DAY_NUM))
            calls = [call(k) for k in raw_results.keys()]
            mock_fetch_member.assert_has_awaits(calls)


all_ave_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
f'''```Wordle Average Leaderboard: {TEST_DATE - datetime.timedelta(days=TEST_DAY_NUM):%d/%m/%Y} - {TEST_DATE_BEFORE:%d/%m/%Y}
===========================================
POS NAME           SCORE  TOTAL GAMES
-------------------------------------------
1   1029           3.000  1```''')
week_ave_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
f'''```Wordle Average Leaderboard: {TEST_DATE_BEFORE - datetime.timedelta(days=TEST_DATE_BEFORE.isoweekday()):%d/%m/%Y} - {TEST_DATE_BEFORE:%d/%m/%Y}
===========================================
POS NAME           SCORE  TOTAL GAMES
-------------------------------------------
1   1029           3.000  1```''')
month_ave_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
f'''```Wordle Average Leaderboard: {TEST_DATE_BEFORE - datetime.timedelta(days=TEST_DATE_BEFORE.day):%d/%m/%Y} - {TEST_DATE_BEFORE:%d/%m/%Y}
===========================================
POS NAME           SCORE  TOTAL GAMES
-------------------------------------------
1   1029           3.000  1```''')
five_day_ave_test_output = (wc.WordleCommandHandler.Response.MSG_CHANNEL,
f'''```Wordle Average Leaderboard: {TEST_DATE - datetime.timedelta(days=5):%d/%m/%Y} - {TEST_DATE_BEFORE:%d/%m/%Y}
===========================================
POS NAME           SCORE  TOTAL GAMES
-------------------------------------------
1   1029           3.000  1```''')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'additional,calls_db,days,raw_results,test_output',
    [
        pytest.param(None, True, TEST_DAY_NUM, normal_raw_results, all_ave_test_output,
                     id='No additional commands'),
        pytest.param([], True, TEST_DAY_NUM, normal_raw_results, all_ave_test_output,
                     id='Empty additional commands'),
        pytest.param(['week'], True, TEST_DATE.isoweekday(), normal_raw_results, week_ave_test_output,
                     id='Week average leaderboard request'),
        pytest.param(['month'], True, TEST_DATE.day, normal_raw_results, month_ave_test_output,
                     id='Month average leaderboard request'),
        pytest.param(['5'], True, 5, normal_raw_results, five_day_ave_test_output, id='Days average leaderboard request'),
        pytest.param(['all'], True, TEST_DAY_NUM, normal_raw_results, all_ave_test_output,
                     id='All average leaderboard request'),
        pytest.param(['invalid'], False, 0, None, invalid_test_output, id='Invalid average leaderboard request')
    ]
)
async def test_average_ldb(additional, calls_db, days, raw_results, test_output):
    with patch.object(discord.Guild, 'fetch_member') as mock_fetch_member, \
            patch('wordle_buddy.json_db.JsonWordleDB') as MockDB, \
            patch('wordle_buddy.utils.current_day') as mock_current_day, \
            patch(f'{wc.__name__}.datetime', wraps=datetime) as mock_dt:
        guild_inst = discord.Guild
        guild_inst.id = 99
        mock_db = MockDB.return_value
        if calls_db:
            mock_fetch_member.side_effect = [DummyMem(str(k)) for k in raw_results.keys()]
            mock_db.load.return_value = raw_results
        mock_current_day.return_value = TEST_DAY_NUM
        mock_dt.datetime.today.return_value = TEST_DATE
        handler = wc.WordleCommandHandler(mock_db)
        assert await handler._average_ldb(guild_inst, additional) == test_output
        if calls_db:
            mock_db.load.assert_called_once_with(99, weeks=range(TEST_DAY_NUM - days, TEST_DAY_NUM))
            calls = [call(k) for k in raw_results.keys()]
            mock_fetch_member.assert_has_awaits(calls)


normal_ldb_results = {1029: [{'score': 7}, {'score': 3}], 1028: [{'score': 4}, {'score': 1}], 1027: [{'score': 5}, {'score': 3}]}
normal_expected_output = {'1028': 5, '1027': 8, '1029': 10}
none_ldb_results = {1029: [None]}
none_expected_output = {'1029': 7}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_results,expected_output',
    [
        pytest.param(normal_ldb_results, normal_expected_output,
                     id='Normal input produces good output'),
        pytest.param(none_ldb_results, none_expected_output,
                     id='None input produces 7 score output')
    ]
)
async def test_ldb_from_results(test_results, expected_output):
    with patch.object(discord.Guild, 'fetch_member') as mock_fetch_member:
        mock_guild = discord.Guild
        mock_fetch_member.side_effect = [DummyMem(str(k)) for k in test_results.keys()]
        assert await wc._ldb_from_results(
            mock_guild, test_results) == expected_output
        calls = [call(k) for k in test_results.keys()]
        mock_fetch_member.assert_has_awaits(calls)


normal_ave_expected = {'1028': (2.5, 2), '1027': (4, 2), '1029': (5, 2)}
none_ave_results = {1029: [{'score': 7}, None], 1028: [{'score': 4}, {'score': 1}], 1027: [{'score': 5}, {'score': 3}]}
none_ave_expected = {'1028': (2.5, 2), '1027': (4, 2), '1029': (7, 1)}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_results,expected_output',
    [
        pytest.param(normal_ldb_results, normal_ave_expected,
                     id='Normal input produces good average output'),
        pytest.param(none_ave_results, none_ave_expected,
                     id='None input not scored for average output')
    ]
)
async def test_ave_ldb_from_results(test_results, expected_output):
    with patch.object(discord.Guild, 'fetch_member') as mock_fetch_member:
        mock_guild = discord.Guild
        mock_fetch_member.side_effect = [DummyMem(str(k)) for k in test_results.keys()]
        assert await wc._ave_ldb_from_results(
            mock_guild, test_results) == expected_output
        calls = [call(k) for k in test_results.keys()]
        mock_fetch_member.assert_has_awaits(calls)


def test_help():
    handler = wc.WordleCommandHandler(None)
    assert handler._help() == (handler.Response.MSG_PRIVATE, wc.HELP_TEXT)
