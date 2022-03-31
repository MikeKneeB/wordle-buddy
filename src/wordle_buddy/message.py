import re
from wordle_buddy import utils
from datetime import datetime
from time import time


WORDLE_HEADER_RE = re.compile(r'Wordle (\d+) ([123456X])/6[*]?')


class MessageException(Exception):

    def __init__(self, reason):
        self.reason = reason


def get_matrix(result_lines):
    matrix = []
    for line in result_lines:
        line = line.strip()
        if len(line) == 5:
            this_line = list(map(lambda x: utils.EMOJI_TO_RESULT[x], line.strip()))
            matrix.append(this_line)
        else:
            raise MessageException('Wrong number of characters in results line')
    return matrix


def process_header(header):
    header_match = WORDLE_HEADER_RE.match(header.strip())
    if header_match:
        if header_match.group(2) == 'X':
            return int(header_match.group(1)), utils.FAILURE_SCORE
        else:
            return int(header_match.group(1)), int(header_match.group(2))
    raise MessageException('No header for message')


def datetime_from_utc(utc_time):
    stamp = time()
    offset = datetime.fromtimestamp(stamp) - datetime.utcfromtimestamp(stamp)
    return utc_time + offset


def validate(result, date):
    if utils.that_day(datetime_from_utc(date)) != result['week_number']:
        raise MessageException('Bad week number (don\'t be late)!')
    if result['score'] != utils.FAILURE_SCORE:
        if len(result['matrix']) != result['score']:
            raise MessageException('Score and matrix length were different')
        if sum(result['matrix'][-1]) != 10:
            raise MessageException('Result didn\'t end in a success')
    elif sum(result['matrix'][-1]) == 10:
        raise MessageException('Result did end in a success, but was reported as a failure')


class WordleMessageManager:

    HEADER_LINES = 2

    def __init__(self, db):
        self._database = db

    def handle(self, guild, name, message, date):
        lines = message.split('\n')
        if len(lines) > self.HEADER_LINES:
            try:
                week_number, score = process_header(lines[0])
                result = {
                    'week_number': week_number,
                    'score': score,
                    'matrix': get_matrix([line for line in lines[self.HEADER_LINES:] if line.strip()])
                }
                validate(result, date)
                self._database.save(guild, name, result)
                return True
            except MessageException as me:
                print(f'Message exception: {me.reason}')
            except KeyError:
                print(f'Key error: bad character in result matrix')
        return False
