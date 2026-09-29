"""End-to-end checks of app.py using Streamlit's headless AppTest runner.

These cover the state bugs that live in app.py rather than logic_utils.py.
"""
from streamlit.testing.v1 import AppTest


def start(secret=50, difficulty="Normal"):
    at = AppTest.from_file("app.py")
    at.run()
    if difficulty != "Normal":
        at.selectbox[0].select(difficulty)
        at.run()
    at.session_state["secret"] = secret
    return at


def guess(at, value):
    at.text_input[0].input(str(value))
    at.button[0].click()
    at.run()
    return at


def click(at, label_start):
    next(b for b in at.button if b.label.startswith(label_start)).click()
    at.run()
    return at


def info_text(at):
    return at.info[0].value


def test_fresh_game_shows_full_attempts_and_correct_range():
    at = start()
    expected = "Guess a number between 1 and 100. Attempts left: 8"
    assert info_text(at) == expected


def test_attempts_left_updates_on_the_same_turn():
    at = guess(start(), 10)
    # Must agree with the real counter, not lag one turn behind it
    left = 8 - at.session_state["attempts"]
    assert info_text(at).endswith(f"Attempts left: {left}")
    assert left == 7


def test_hint_direction_in_the_live_app():
    at = guess(start(secret=47), 80)
    assert "LOWER" in at.warning[0].value


def test_even_attempt_uses_numeric_comparison():
    at = start(secret=50)
    guess(at, 10)
    guess(at, 9)  # second guess: used to be compared as the string "9" > "50"
    assert "HIGHER" in at.warning[0].value
    assert at.session_state["score"] == -10


def test_player_gets_every_allowed_guess():
    at = start(secret=50)
    for g in range(1, 8):
        guess(at, g)
    assert at.session_state["status"] == "playing"
    guess(at, 8)
    assert at.session_state["status"] == "lost"


def test_new_game_after_win_really_restarts():
    at = guess(start(secret=50), 50)
    assert at.session_state["status"] == "won"
    click(at, "New Game")
    assert at.session_state["status"] == "playing"
    assert at.session_state["score"] == 0
    assert at.session_state["attempts"] == 0
    assert at.session_state["history"] == []
    assert not any("already won" in s.value for s in at.success)


def test_new_game_secret_respects_difficulty():
    at = start(difficulty="Easy")
    for _ in range(30):
        click(at, "New Game")
        assert 1 <= at.session_state["secret"] <= 20


def test_switching_difficulty_resets_secret_into_new_range():
    at = start(secret=80)
    at.selectbox[0].select("Easy")
    at.run()
    assert 1 <= at.session_state["secret"] <= 20
    assert "between 1 and 20" in info_text(at)


def test_invalid_input_does_not_use_an_attempt():
    at = guess(start(), "abc")
    assert at.error[0].value == "That is not a number."
    assert at.session_state["attempts"] == 0
    assert info_text(at).endswith("Attempts left: 8")
