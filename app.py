import random

import streamlit as st

# FIX: game logic refactored from app.py into logic_utils.py using Claude Code
# (agent mode) so it can be unit tested without Streamlit.
from logic_utils import (
    build_round_record,
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    parse_guess,
    summarize_rounds,
    update_score,
)


def start_new_game(difficulty: str) -> None:
    """Reset every piece of game state for a fresh round."""
    # FIX: New Game used to reset only attempts and secret (always 1-100), so
    # status stayed "won"/"lost" and the game was stuck. Claude pulled all of
    # the resets into one function that respects the difficulty range.
    low, high = get_range_for_difficulty(difficulty)
    st.session_state.secret = random.randint(low, high)
    # FIX: attempts starts at 0 (was 1 on first load), so Normal gives all 8.
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    # Challenge 2/4: one record per valid guess, for the sidebar and summary.
    st.session_state.rounds = []
    st.session_state.difficulty = difficulty


def show_hot_cold(record: dict) -> None:
    """Challenge 4: show a color-coded Hot/Cold line for the last guess."""
    st.markdown(
        f"### :{record['color']}[{record['emoji']} {record['temperature']}!]"
    )


def show_guess_history(rounds: list, reveal_closeness: bool) -> None:
    """Challenge 2: sidebar list of past guesses and how close each was."""
    st.sidebar.divider()
    st.sidebar.subheader("📜 Guess History")
    if not rounds:
        st.sidebar.caption("No guesses yet.")
        return
    for number, r in enumerate(rounds, start=1):
        if reveal_closeness:
            st.sidebar.markdown(
                f"**#{number}: {r['guess']}** :{r['color']}[{r['emoji']} "
                f"{r['temperature']}]"
            )
            st.sidebar.progress(
                r["closeness"], text=f"{r['closeness']:.0%} close"
            )
        else:
            st.sidebar.markdown(f"**#{number}: {r['guess']}**")
    if not reveal_closeness:
        st.sidebar.caption("Turn on 'Show hint' to see how close you were.")


def show_summary(rounds: list) -> None:
    """Challenge 4: end-of-game table of every guess in the session."""
    st.subheader("📊 Game Summary")
    st.table(summarize_rounds(rounds))


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = get_attempt_limit(difficulty)
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FIX: switching difficulty now starts a new game, so the secret is always
# inside the current range (it used to keep e.g. 80 on Easy's 1-20).
if st.session_state.get("difficulty") != difficulty:
    start_new_game(difficulty)
st.session_state.setdefault("rounds", [])

st.subheader("Make a guess")

# FIX: these are placeholders filled in at the end of the script, after the
# guess is processed. Before, they rendered first and always showed the
# previous turn's attempts/history.
status_box = st.empty()
debug_box = st.expander("Developer Debug Info")

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game(difficulty)
    st.success("New game started.")

if st.session_state.status == "playing" and submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: invalid input no longer uses up an attempt.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: always compare int to int. The old code turned the secret into
        # a string on even attempts, which made comparisons alphabetical.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )
        record = build_round_record(
            guess_int, st.session_state.secret, outcome,
            st.session_state.score, low, high,
        )
        st.session_state.rounds.append(record)

        if show_hint:
            st.warning(message)
            if outcome != "Win":
                show_hot_cold(record)

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )
elif st.session_state.status == "won":
    st.success("You already won. Start a new game to play again.")
elif st.session_state.status == "lost":
    st.error("Game over. Start a new game to try again.")

if st.session_state.status != "playing" and st.session_state.rounds:
    show_summary(st.session_state.rounds)

show_guess_history(st.session_state.rounds, reveal_closeness=show_hint)

# FIX: range comes from the difficulty instead of a hard-coded "1 and 100".
status_box.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with debug_box:
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
