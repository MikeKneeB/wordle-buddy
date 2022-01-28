import datetime

import pytest
from wordle_buddy import commands as wc

from unittest.mock import patch

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
        mock_dt.datetime.today.return_value = datetime.datetime(day=27, month=1, year=2021)
        assert wc._ldb_message(*test_input) == test_output


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'test_input,test_output',
    [
        pytest.param(
            '',
            (wc.WordleCommandHandler.Response.NONE, None),
            id='Empty message returns NONE'),
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


def test_help():
    handler = wc.WordleCommandHandler(None)
    assert handler._help() == (handler.Response.MSG_PRIVATE, wc.HELP_TEXT)

