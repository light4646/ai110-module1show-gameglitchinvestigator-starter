import pytest

from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# --- Starter tests ---------------------------------------------------------
# FIX: the AI-written starter tests compared check_guess(...) directly to a
# string, but check_guess returns (outcome, message). Unpacked the tuple.

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Bug 1: hint messages pointed the wrong way ----------------------------

def test_too_high_guess_tells_player_to_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_guess_tells_player_to_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


# --- Bug 2: string comparison on even attempts ------------------------------

def test_single_digit_guess_is_compared_numerically():
    # "9" > "50" alphabetically, but 9 < 50 numerically
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


def test_large_guess_is_compared_numerically():
    # "100" < "50" alphabetically, but 100 > 50 numerically
    outcome, _ = check_guess(100, 50)
    assert outcome == "Too High"


# --- Bug 5: difficulty ranges ------------------------------------------------

def test_hard_range_is_wider_than_normal():
    n_low, n_high = get_range_for_difficulty("Normal")
    h_low, h_high = get_range_for_difficulty("Hard")
    assert (h_high - h_low) > (n_high - n_low)


def test_difficulty_gets_harder_in_order():
    levels = ("Easy", "Normal", "Hard")
    sizes = [get_range_for_difficulty(d)[1] for d in levels]
    assert sizes == sorted(sizes)


def test_attempt_limits_match_sidebar():
    assert get_attempt_limit("Easy") == 6
    assert get_attempt_limit("Normal") == 8
    assert get_attempt_limit("Hard") == 5


def test_unknown_difficulty_falls_back_to_normal():
    normal = get_range_for_difficulty("Normal")
    assert get_range_for_difficulty("Impossible") == normal


# --- Bug 6: scoring ----------------------------------------------------------

def test_first_try_win_gets_full_points():
    assert update_score(0, "Win", attempt_number=1) == 100


def test_win_points_drop_each_attempt_but_never_below_minimum():
    assert update_score(0, "Win", attempt_number=3) == 80
    assert update_score(0, "Win", attempt_number=20) == 10


@pytest.mark.parametrize("attempt", [1, 2, 3, 4])
@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
def test_wrong_guess_always_costs_points(outcome, attempt):
    assert update_score(50, outcome, attempt_number=attempt) == 45


# --- Bug 7 + edge cases: parse_guess ----------------------------------------

def test_valid_guess_parses():
    assert parse_guess("42", 1, 100) == (True, 42, None)


def test_surrounding_whitespace_is_ignored():
    assert parse_guess("  42  ", 1, 100) == (True, 42, None)


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_empty_input_is_rejected(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok and value is None and err == "Enter a guess."


@pytest.mark.parametrize("raw", ["abc", "4O", "fifty", "1e2x"])
def test_non_numeric_input_is_rejected(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok and value is None and err == "That is not a number."


@pytest.mark.parametrize("raw", ["49.9", "3.0", "-0.5"])
def test_decimal_input_is_rejected_not_truncated(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok and value is None and "whole number" in err


@pytest.mark.parametrize("raw", ["-5", "0", "101", "99999999999999999999"])
def test_out_of_range_input_is_rejected(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok and value is None and "between 1 and 100" in err


def test_range_bounds_are_inclusive():
    assert parse_guess("1", 1, 100)[0]
    assert parse_guess("100", 1, 100)[0]


def test_no_range_check_when_bounds_not_given():
    assert parse_guess("-5") == (True, -5, None)
