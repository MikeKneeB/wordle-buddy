import datetime

import pytest

from wordle_buddy import message as wm, utils

from contextlib import nullcontext as does_not_raise
from unittest.mock import patch


test_lines = [f'{utils.WHITE_SQUARE_CHAR}{utils.GREEN_SQUARE_CHAR}{utils.BLACK_SQUARE_CHAR}{utils.YELLOW_SQUARE_CHAR}{utils.WHITE_SQUARE_CHAR}']
too_many_lines = [f'{utils.WHITE_SQUARE_CHAR}{utils.GREEN_SQUARE_CHAR}{utils.BLACK_SQUARE_CHAR}{utils.YELLOW_SQUARE_CHAR}{utils.WHITE_SQUARE_CHAR}{utils.WHITE_SQUARE_CHAR}']
too_few_lines = [f'{utils.WHITE_SQUARE_CHAR}{utils.GREEN_SQUARE_CHAR}{utils.BLACK_SQUARE_CHAR}{utils.YELLOW_SQUARE_CHAR}']
bad_char_lines = [f'{utils.WHITE_SQUARE_CHAR}{utils.GREEN_SQUARE_CHAR}{utils.BLACK_SQUARE_CHAR}U{utils.YELLOW_SQUARE_CHAR}']
test_exp = [[0, 2, 0, 1, 0]]


@pytest.mark.parametrize(
    'test_input,test_output,expectation',
    [
        pytest.param(test_lines, test_exp, does_not_raise(), id="Good input"),
        pytest.param([], [], does_not_raise(), id="Empty input"),
        pytest.param(too_many_lines, None, pytest.raises(wm.MessageException), id="Too many lines"),
        pytest.param(too_few_lines, None, pytest.raises(wm.MessageException), id="Too few lines"),
        pytest.param(bad_char_lines, None, pytest.raises(KeyError), id="Bad character")
    ]
)
def test_get_matrix(test_input, test_output, expectation):
    with expectation:
        assert wm.get_matrix(test_input) == test_output


normal_input = 'Wordle 321 3/6'
normal_output = (321, 3)
hard_input = 'Wordle 321 3/6*'
hard_output = (321, 3)
failed_input = 'Wordle 321 X/6*'
failed_output = (321, 7)
bad_text_input = 'Wurdle 321 X/6*'
bad_week_input = 'Wordle 3u1 X/6*'
bad_score_low_input = 'Wordle 321 0/6*'
bad_score_high_input = 'Wordle 321 7/6*'
bad_score_end_input = 'Wordle 321 4/7'


@pytest.mark.parametrize(
    'test_input,test_output,expectation',
    [
        pytest.param(normal_input, normal_output, does_not_raise(), id="Normal mode header processed"),
        pytest.param(hard_input, hard_output, does_not_raise(), id="Hard mode header processed"),
        pytest.param(failed_input, failed_output, does_not_raise(), id="Failure header processed"),
        pytest.param(bad_text_input, None, pytest.raises(wm.MessageException), id="Bad text raises exception"),
        pytest.param(bad_week_input, None, pytest.raises(wm.MessageException), id="Bad week number raises exception"),
        pytest.param(bad_score_low_input, None, pytest.raises(wm.MessageException),
                     id="Score too low raises exception"),
        pytest.param(bad_score_high_input, None, pytest.raises(wm.MessageException),
                     id="Score too high raises exception"),
        pytest.param(bad_score_end_input, None, pytest.raises(wm.MessageException),
                     id="Incorrect 'out of' raises exception"),
    ]
)
def test_process_header(test_input, test_output, expectation):
    with expectation:
        assert wm.process_header(test_input) == test_output


result_ok = {
    'week_number': 321,
    'score': 3,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [2, 2, 2, 2, 2]]
}
result_fail_ok = {
    'week_number': 321,
    'score': 7,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [0, 1, 0, 2, 0],
               [0, 1, 0, 2, 0],
               [0, 1, 0, 2, 0],
               [0, 1, 0, 2, 0]]
}
result_bad_date = {
    'week_number': 318,
    'score': 3,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [2, 2, 2, 2, 2]]
}
result_bad_score = {
    'week_number': 321,
    'score': 4,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [2, 2, 2, 2, 2]]
}
result_bad_matrix = {
    'week_number': 321,
    'score': 3,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [2, 0, 2, 2, 2]]
}
result_bad_fail = {
    'week_number': 321,
    'score': 7,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [2, 2, 2, 2, 2]]
}


@pytest.mark.parametrize(
    'test_input,expectation',
    [
        pytest.param(result_ok, does_not_raise(), id="Good result does not except"),
        pytest.param(result_fail_ok, does_not_raise(), id="Good failure result does not except"),
        pytest.param(result_bad_date, pytest.raises(wm.MessageException), id="Bad date raises exception"),
        pytest.param(result_bad_fail, pytest.raises(wm.MessageException),
                     id="Failed score but passed matrix raises exception"),
        pytest.param(result_bad_matrix, pytest.raises(wm.MessageException),
                     id="Matrix doesn't end in a success but score does raises exception"),
        pytest.param(result_bad_score, pytest.raises(wm.MessageException),
                     id="Score doesn't match matrix raises exception"),
        pytest.param(result_bad_score, pytest.raises(wm.MessageException),
                     id="Score doesn't match matrix raises exception"),
    ]
)
def test_validate(test_input, expectation):
    with patch('wordle_buddy.utils.that_day') as mock_that_day:
        mock_that_day.return_value = 321
        date = datetime.datetime(year=2021, month=1, day=1)
        with expectation:
            wm.validate(test_input, date)


result_ok_bst = {
    'week_number': 285,
    'score': 3,
    'matrix': [[0, 0, 0, 0, 0],
               [0, 1, 0, 2, 0],
               [2, 2, 2, 2, 2]]
}


def test_validate_bst():
    date = datetime.datetime(year=2022, month=3, day=30, hour=23, minute=30)
    with does_not_raise():
        wm.validate(result_ok_bst, date)


good_inputs = (
    1337,
    10101,
    f'''Wordle 321 3/6

\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c
\u2b1c\U0001f7e8\u2b1c\U0001f7e9\u2b1c
\U0001f7e9\U0001f7e9\U0001f7e9\U0001f7e9\U0001f7e9
''',
    datetime.datetime(year=2021, month=1, day=1)
)
good_result = (
    1337,
    10101,
    {
        'week_number': 321,
        'score': 3,
        'matrix': [[0, 0, 0, 0, 0],
                   [0, 1, 0, 2, 0],
                   [2, 2, 2, 2, 2]]
    }
)

no_body_inputs = (
    1337,
    10101,
    f'''Wordle 321 3/6
''',
    datetime.datetime(year=2021, month=1, day=1)
)

bad_header_inputs = (
    13337,
    10101,
    f'''Wurdle 321 3/6

\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c
\u2b1c\U0001f7e8\u2b1c\U0001f7e9\u2b1c
\U0001f7e9\U0001f7e9\U0001f7e9\U0001f7e9\U0001f7e9
''',
    datetime.datetime(year=2021, month=1, day=1)
)

bad_matrix_inputs = (
    1337,
    10101,
    f'''Wordle 321 3/6

\u2b1c\u2b1c\u2b1c\u2b1c\u2b1c
\u2b1c\U0001f7e8\u2b1c\U0001f7e9\u2b1c
\U0001f7e9\U0001f7e91\U0001f7e9\U0001f7e9
''',
    datetime.datetime(year=2021, month=1, day=1)
)


@pytest.mark.parametrize(
    'test_input,test_output,db_called_with',
    [
        pytest.param(good_inputs, True, good_result, id='Good input succeeds and is saved'),
        pytest.param(no_body_inputs, False, None, id='No body fails and is not saved'),
        pytest.param(bad_header_inputs, False, None, id='Bad header fails and is not saved'),
        pytest.param(bad_matrix_inputs, False, None, id='Bad matrix fails and is not saved')
    ]
)
def test_handle(test_input, test_output, db_called_with):
    with patch('wordle_buddy.utils.that_day') as mock_that_day,\
            patch('wordle_buddy.json_db.JsonWordleDB') as MockDB:
        mock_that_day.return_value = 321

        db_inst = MockDB.return_value
        db_inst.save.return_value = test_output
        man = wm.WordleMessageManager(db_inst)
        assert man.handle(*test_input) == test_output
        if db_called_with:
            db_inst.save.assert_called_once_with(*db_called_with)
        else:
            db_inst.save.assert_not_called()
