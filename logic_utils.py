"""Pure game logic for the Glitchy Guesser number-guessing game.

Everything here is free of Streamlit so it can be unit tested with pytest.
"""

DIFFICULTY_SETTINGS = {
    "Easy": {"range": (1, 20), "attempts": 6},
    "Normal": {"range": (1, 100), "attempts": 8},
    # FIX: Hard used to be 1-50, a smaller (easier) range than Normal.
    # Claude flagged it while reading the code; widened to 1-200.
    "Hard": {"range": (1, 200), "attempts": 5},
}

DEFAULT_DIFFICULTY = "Normal"

WRONG_GUESS_PENALTY = 5
MAX_WIN_POINTS = 100
MIN_WIN_POINTS = 10
POINTS_PER_EXTRA_ATTEMPT = 10


def _settings_for(difficulty: str) -> dict:
    """Return the settings for a difficulty, falling back to Normal."""
    return DIFFICULTY_SETTINGS.get(
        difficulty, DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY]
    )


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive ``(low, high)`` range of secrets for a difficulty.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"`` or ``"Hard"``.
            Unknown values fall back to ``"Normal"``.

    Returns:
        A ``(low, high)`` tuple where ``low <= secret <= high``.
    """
    return _settings_for(difficulty)["range"]


def get_attempt_limit(difficulty: str) -> int:
    """Return how many guesses the player gets for a difficulty.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"`` or ``"Hard"``.
            Unknown values fall back to ``"Normal"``.

    Returns:
        The maximum number of valid guesses allowed in one game.
    """
    return _settings_for(difficulty)["attempts"]


def parse_guess(raw, low: int | None = None, high: int | None = None):
    """Parse the text a player typed into a whole-number guess.

    Surrounding whitespace is ignored. Decimals such as ``"49.9"`` are
    rejected instead of being silently truncated, and when ``low`` and
    ``high`` are given the guess must fall inside that inclusive range.

    Args:
        raw: The raw text from the input box (may be ``None``).
        low: Smallest allowed guess, or ``None`` for no lower bound.
        high: Largest allowed guess, or ``None`` for no upper bound.

    Returns:
        A tuple ``(ok, guess_int, error_message)``. On success ``ok`` is
        ``True``, ``guess_int`` is the parsed ``int`` and ``error_message`` is
        ``None``; on failure ``ok`` is ``False``, ``guess_int`` is ``None`` and
        ``error_message`` explains the problem.
    """
    if raw is None or str(raw).strip() == "":
        return False, None, "Enter a guess."

    text = str(raw).strip()

    # FIX: the old code did int(float(raw)), so "49.9" quietly became 49.
    # Claude (agent mode) changed it to reject decimals with a clear message.
    try:
        value = int(text)
    except ValueError:
        try:
            float(text)
        except ValueError:
            return False, None, "That is not a number."
        return False, None, "Please enter a whole number (no decimals)."

    if low is not None and high is not None and not low <= value <= high:
        return False, None, f"Your guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int):
    """Compare a guess to the secret number.

    Args:
        guess: The player's guess.
        secret: The secret number.

    Returns:
        A tuple ``(outcome, message)`` where ``outcome`` is ``"Win"``,
        ``"Too High"`` or ``"Too Low"`` and ``message`` is the hint to show.
    """
    # FIX: removed the TypeError fallback that compared guess and secret as
    # strings ("9" > "50" is True). Both are always ints now.
    if guess == secret:
        return "Win", "🎉 Correct!"
    # FIX: hint messages were swapped (Too High said "Go HIGHER!").
    # Claude moved this out of app.py and corrected the direction.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Return the new score after a guess.

    A win is worth ``MAX_WIN_POINTS`` on the first guess and
    ``POINTS_PER_EXTRA_ATTEMPT`` fewer for each later guess, never less
    than ``MIN_WIN_POINTS``. Every wrong guess costs ``WRONG_GUESS_PENALTY``.

    Args:
        current_score: The score before this guess.
        outcome: ``"Win"``, ``"Too High"`` or ``"Too Low"``.
        attempt_number: Which guess this was, counting from 1.

    Returns:
        The updated score. Unknown outcomes leave the score unchanged.
    """
    if outcome == "Win":
        # FIX: was 100 - 10 * (attempt_number + 1): a first-try win scored 70.
        extra_attempts = attempt_number - 1
        points = MAX_WIN_POINTS - POINTS_PER_EXTRA_ATTEMPT * extra_attempts
        return current_score + max(points, MIN_WIN_POINTS)

    # FIX: "Too High" used to ADD 5 points on even attempts.
    if outcome in ("Too High", "Too Low"):
        return current_score - WRONG_GUESS_PENALTY

    return current_score
