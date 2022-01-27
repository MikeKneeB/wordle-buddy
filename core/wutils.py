from datetime import date
from enum import Enum


WHITE_SQUARE_CHAR = '\U00002b1c'
BLACK_SQUARE_CHAR = '\U00002b1b'
YELLOW_SQUARE_CHAR = '\U0001f7e8'
GREEN_SQUARE_CHAR = '\U0001f7e9'

DAY_ONE = date(2021, 6, 19)
FAILURE_SCORE = 7


class ResultSquare(Enum):
    GREY = 0
    YELLOW = 1
    GREEN = 2


EMOJI_TO_RESULT = {
    WHITE_SQUARE_CHAR: ResultSquare.GREY.value,
    BLACK_SQUARE_CHAR: ResultSquare.GREY.value,
    YELLOW_SQUARE_CHAR: ResultSquare.YELLOW.value,
    GREEN_SQUARE_CHAR: ResultSquare.GREEN.value
}


def current_day():
    return (date.today() - DAY_ONE).days
