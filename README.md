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
7. Switching the sidebar to **Easy** starts a fresh game with "Guess a number between 1 and 20. Attempts left: 6" (checked headlessly, scenario E in `bug_trace_after.txt`).

The same scenarios, run headlessly before and after the fixes, are in [`bug_trace_before.txt`](bug_trace_before.txt) and [`bug_trace_after.txt`](bug_trace_after.txt).

## 🧪 Test Results

48 tests: unit tests for `logic_utils.py` in `tests/test_game_logic.py`, and headless end-to-end tests of `app.py` using Streamlit's `AppTest` in `tests/test_app_flow.py`. Every app-flow test was also run against the original `app.py`, and all 9 failed there, so they really catch the bugs. Full verbose output is in [`test_results.txt`](test_results.txt).

```
$ pytest
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
rootdir: ai110-module1show-gameglitchinvestigator-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 48 items

tests/test_app_flow.py .........                                         [ 18%]
tests/test_game_logic.py .......................................         [100%]

============================== 48 passed in 0.81s ==============================
```

## 🚀 Stretch Features

- [x] **Challenge 1: Advanced Edge-Case Testing.** `parse_guess` is tested against empty and whitespace-only input, non-numeric strings (`"abc"`, `"4O"` with a letter O, `"fifty"`), decimals (`"49.9"`, `"3.0"`, `"-0.5"`), negatives and zero, above-range values and a 20-digit number, plus inclusive bounds. The prompts and the reason for each edge case are in [`ai_interactions.md`](ai_interactions.md).
- [x] **Challenge 3: Professional Documentation and Linting.** Every function in `logic_utils.py` has a Google-style docstring. `pycodestyle` (PEP 8) and `pydocstyle` report no issues. Before/after linter output is in [`lint_report.txt`](lint_report.txt), and the changes are described in [`ai_interactions.md`](ai_interactions.md).
- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
