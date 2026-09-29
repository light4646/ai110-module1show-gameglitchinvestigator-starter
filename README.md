# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python -m streamlit run app.py`
3. Run the tests: `pytest`
4. *(Optional)* Replay the bug scenarios headlessly: `python scripts/reproduce_bugs.py`

> If you edit `logic_utils.py` while the app is running, restart `streamlit run`. Streamlit re-runs `app.py` on save but keeps already-imported modules in memory.

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] Describe the game's purpose.
- [x] Detail which bugs you found.
- [x] Explain what fixes you applied.

### Purpose

Glitchy Guesser is a Streamlit number-guessing game. The app picks a secret number in a range set by the difficulty (Easy 1–20, Normal 1–100, Hard 1–200). You get a limited number of guesses (6 / 8 / 5), and after each guess a hint tells you to go higher or lower. Your score starts at 0: each wrong guess costs 5 points, and a win adds 100 points minus 10 for every guess after the first (minimum 10).

### Bugs found

The starter was AI-generated and "production-ready" in name only. I found 7 bugs. Full details, reproduction steps and a Bug Reproduction Log are in [`reflection.md`](reflection.md) section 1, with a raw trace in [`bug_trace_before.txt`](bug_trace_before.txt).

| # | Bug | Root cause |
|---|-----|------------|
| 1 | Hints backwards: a guess of 80 vs secret 47 said "Go HIGHER!" | Messages swapped in `check_guess` |
| 2 | The same guess got different hints on alternate turns | `app.py` turned the secret into a `str` on even attempts; the `TypeError` fallback compared `"9" > "50"` alphabetically |
| 3 | Only 7 guesses on Normal (should be 8); "Attempts left" one turn behind | `attempts` started at 1, and the info box rendered before the guess was processed |
| 4 | New Game after a win stayed stuck on "You already won" | New Game didn't reset `status`, `score` or `history` |
| 5 | Hard (1–50) easier than Normal; New Game and difficulty switching ignored the range; prompt hard-coded to "1 and 100" | Wrong range in `get_range_for_difficulty`, `randint(1, 100)` in New Game, secret never regenerated |
| 6 | Wrong "Too High" guesses *gained* 5 points on even turns; a first-try win scored only 70 | `update_score` parity check and an off-by-one in the win formula |
| 7 | "abc" still used up a turn; "49.9" silently became 49 | `attempts += 1` ran before validation; `int(float(raw))` |

### Fixes applied

- **Refactor:** `get_range_for_difficulty`, `parse_guess`, `check_guess` and `update_score` now live in [`logic_utils.py`](logic_utils.py) with no Streamlit code, so pytest can test them directly. `app.py` imports them. Difficulty settings are in one `DIFFICULTY_SETTINGS` table, and a new `get_attempt_limit` reads from it.
- **Hints (bugs 1, 2):** `check_guess` returns "📉 Go LOWER!" for Too High and "📈 Go HIGHER!" for Too Low. The `str()` conversion and the string-comparison fallback are gone, so it always compares int to int.
- **Attempts (bugs 3, 7):** `attempts` starts at 0 and only goes up for a *valid* guess. The status box and debug panel are placeholders (`st.empty()` / `st.expander`) filled in at the end of the script, so they show the current turn.
- **New Game and difficulty (bugs 4, 5):** A single `start_new_game(difficulty)` resets secret, attempts, score, status and history, and picks the secret from the difficulty's range. Changing the difficulty calls it too. Hard is now 1–200, and the prompt shows the real range.
- **Scoring (bug 6):** Every wrong guess costs 5. A win is worth `100 - 10 × (guess number - 1)`, with a minimum of 10.
- **Input (bug 7):** `parse_guess` trims whitespace and rejects empty, non-numeric, decimal and out-of-range input with a clear message.

Each fix has a `# FIX:` comment next to it in the code.

## 📸 Demo Walkthrough

A real game played in the browser after the fixes (Normal, Developer Debug Info open, secret 55):

1. The game loads with "Guess a number between 1 and 100. Attempts left: 8". The debug panel shows Attempts 0, Score 0, History [].
2. User enters **80** and clicks Submit → "📉 Go LOWER!". Attempts left drops to 7 on the same turn, score is −5, history [80].
3. User enters **40** → "📈 Go HIGHER!". Attempts left: 6, score −10.
4. User enters **55** → "🎉 Correct!", balloons, and "You won! The secret was 55. Final score: 70" (−5 −5 + 80 for a win on the 3rd guess).
5. User clicks **New Game 🔁** → "New game started." A new secret is picked (72). Attempts left is back to 8, score 0, history [], and the game is playable again. Before the fix it stayed stuck on "You already won".
6. In the new game, entering **abc** shows "That is not a number." and entering **49.9** shows "Please enter a whole number (no decimals)." Attempts left stays at 8 both times.
7. **With the UI features:** in a later game (secret 60), guessing **95** and then **63** filled the sidebar's 📜 Guess History with "#1: 95 🧊 Cold, 65% close" and "#2: 63 🔥 Hot, 97% close". Guessing **60** won and showed the 📊 Game Summary table (in the Stretch Features section below). After **New Game**, the sidebar said "No guesses yet.", and a guess of **1** showed "📈 Go HIGHER!" followed by a violet **🧊 Cold!**.
8. Switching the sidebar to **Easy** starts a fresh game with "Guess a number between 1 and 20. Attempts left: 6" (checked headlessly, scenario E in `bug_trace_after.txt`).

The same scenarios, run headlessly before and after the fixes, are in [`bug_trace_before.txt`](bug_trace_before.txt) and [`bug_trace_after.txt`](bug_trace_after.txt).

## 🧪 Test Results

63 tests: unit tests for `logic_utils.py` in `tests/test_game_logic.py`, and headless end-to-end tests of `app.py` using Streamlit's `AppTest` in `tests/test_app_flow.py`. The 9 app-flow tests for the original bugs were also run against the original `app.py`, and all 9 failed there, so they really catch the bugs. Full verbose output is in [`test_results.txt`](test_results.txt).

```
$ pytest
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
rootdir: ai110-module1show-gameglitchinvestigator-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 63 items

tests/test_app_flow.py ..............                                    [ 22%]
tests/test_game_logic.py ............................................... [ 96%]
..                                                                       [100%]

============================== 63 passed in 1.08s ==============================
```

## 🚀 Stretch Features

All five challenges are done.

- [x] **Challenge 1: Advanced Edge-Case Testing.** `parse_guess` is tested against empty and whitespace-only input, non-numeric strings (`"abc"`, `"4O"` with a letter O, `"fifty"`), decimals (`"49.9"`, `"3.0"`, `"-0.5"`), negatives and zero, above-range values and a 20-digit number, plus inclusive bounds. All pass (output above). The prompts and the reason for each edge case are in [`ai_interactions.md`](ai_interactions.md#test-generation-sf7).
- [x] **Challenge 2: Feature Expansion (Guess History sidebar).** The sidebar lists every guess in the current game with its Hot/Cold label and a "% close" progress bar showing how near it was to the secret. It clears on New Game, and only shows guess numbers when "Show hint" is off, so it can't leak the answer. The agent workflow (files modified, what was asked, what the agent did, manual corrections) is in [`ai_interactions.md`](ai_interactions.md#agent-workflow-sf8).
- [x] **Challenge 3: Professional Documentation and Linting.** Every function in `logic_utils.py` has a Google-style docstring. `pycodestyle` (PEP 8) and `pydocstyle` report no issues. Before/after linter output is in [`lint_report.txt`](lint_report.txt), and the changes are described in [`ai_interactions.md`](ai_interactions.md#linting--style-sf9).
- [x] **Challenge 4: Enhanced Game UI.** See below.
- [x] **Challenge 5: AI Model Comparison.** The same bug was given to Claude Sonnet 5.5 and Claude Haiku 4.5. Both fixes were run on the same inputs, and the comparison (which was more Pythonic, which explained it better) is in [`ai_interactions.md`](ai_interactions.md#model-comparison-sf11). Raw answers are in [`model_comparison/`](model_comparison/).

### 🎨 Enhanced UI (Challenge 4)

The UI changes sit on top of the core logic. The direction hint (`st.warning` with "Go HIGHER/LOWER") is unchanged, and all the original tests still pass.

| Enhancement | What the player sees | Code |
|---|---|---|
| **Hot/Cold hints with emojis** | After each wrong guess, a line like **🔥 Hot!**, **♨️ Warm!**, **🌬️ Cool!** or **🧊 Cold!**, based on the distance as a share of the range. Being 3 away means the same "heat" on Easy (1–20) and Hard (1–200) | `get_temperature()` and `TEMPERATURE_BANDS` in `logic_utils.py`; `show_hot_cold()` in `app.py` |
| **Color-coded hints** | Each temperature has its own color: Hot is red, Warm orange, Cool blue, Cold violet (Streamlit `:color[...]` markdown). The same colors are used in the sidebar | The `color` field in `TEMPERATURE_BANDS`; `show_hot_cold()` and `show_guess_history()` in `app.py` |
| **Closeness bars** | Each guess in the Guess History sidebar has a progress bar, like "97% close" | `get_closeness()` in `logic_utils.py`; `show_guess_history()` in `app.py` |
| **Session summary table** | When the game ends (win or loss), a **📊 Game Summary** table lists Guess #, Guess, Result, Off by, Hot/Cold and running Score | `build_round_record()` and `summarize_rounds()` in `logic_utils.py`; `show_summary()` in `app.py` |

Example summary from a real game (secret 60):

| Guess # | Guess | Result | Off by | Hot/Cold | Score |
|---|---|---|---|---|---|
| 1 | 95 | Too High | 35 | 🧊 Cold | -5 |
| 2 | 63 | Too High | 3 | 🔥 Hot | -10 |
| 3 | 60 | Win | 0 | 🎯 Correct | 70 |
