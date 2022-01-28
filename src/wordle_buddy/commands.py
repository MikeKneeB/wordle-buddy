import datetime
from enum import Enum
from wordle_buddy import utils

HELP_TEXT = '''
*Hello it's me, the Wordle Buddy!*

I can't do much right now, I'm sorry :(

**Commands:**

Commands begin with '+w' followed by the command list separated by spaces, e.g.:
  +w help
  +w leaderboard 7
  
Available commands:

> help
Get this help message sent to your DMs

> leaderboard [option]
Get a leaderboard sent to the wordle chat channel. Option defines the type of leaderboard, valid options 'week' (default), 'month', or a number of days. 'week' totals scores from the start of the week, 'month' from the start of the month and a number totals scores for the specified number of days (not including the current day).
  
**Results:**

Results are accepted if they are directly copied and pasted from wordle. You can use light or dark mode, it doesn't matter. You have to submit results on the correct day or they will be rejected! If your results have been read and saved by me I will react with a green tick.
'''


async def _ldb_from_results(guild, results):
    ldb = {}
    for k, v in results.items():
        member = await guild.fetch_member(k)
        if member:
            ldb[member.display_name] = _total_score(v)
    sort_ldb = dict(sorted(ldb.items(), key=lambda pair: pair[1]))
    return sort_ldb


def _ldb_message(days, ldb):
    start = datetime.datetime.today() - datetime.timedelta(days=days)
    end = datetime.datetime.today() - datetime.timedelta(days=1)
    ldb_str = f'''```Wordle Leaderboard: {start:%d/%m/%Y} - {end:%d/%m/%Y}
===========================================
POS NAME           SCORE
-------------------------------------------'''
    for num, entry in enumerate(ldb.items(), start=1):
        ldb_str += f'\n{num:<4}{entry[0]:<15}{entry[1]}'
    ldb_str += '```'
    return ldb_str


def _total_score(user_results):
    score = 0
    for result in user_results:
        if result:
            score += result['score']
        else:
            score += utils.FAILURE_SCORE
    return score


class WordleCommandHandler:
    COMMAND_PREFIX = '+w'
    COMMAND_HELP = 'help'
    COMMAND_LEADERBOARD = 'leaderboard'

    class Response(Enum):
        NONE = 0
        MSG_PRIVATE = 1
        MSG_CHANNEL = 2

    def __init__(self, db):
        self._database = db

    async def handle_command(self, guild, message):
        if not message.content.startswith(self.COMMAND_PREFIX):
            return self.Response.NONE, None
        try:
            command_list = message.content.split()[1:]
            if command_list[0] == self.COMMAND_HELP:
                return self._help()
            elif command_list[0] == self.COMMAND_LEADERBOARD:
                command_list.pop(0)
                return await self._leaderboard(guild, command_list)
        except KeyError:
            return self.Response.NONE, None

    def _help(self):
        return self.Response.MSG_PRIVATE, HELP_TEXT

    async def _leaderboard(self, guild, additional=None):
        if additional is None:
            additional = []
        days = datetime.datetime.today().weekday()
        results = self._database.load(guild,
                                      weeks=range(utils.current_day() - days, utils.current_day()))
        ldb = await _ldb_from_results(guild, results)
        return self.Response.MSG_CHANNEL, _ldb_message(ldb)
