# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

AI tool used for everything below: **Claude Code (Claude Opus 5.5), agent mode**, in the Claude desktop app.

The actual prompts I gave the agent were *"okay now fully do proj one"* (core project, SF7, SF9) and later *"do all"* / *"i want the full 28 points"* (SF8, SF4 UI, SF11), with the course rubric saved as a checklist. The "prompts" below are the sub-tasks the agent broke that into (paraphrased), so it's clear what each step was asked to do.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Sub-task prompts (paraphrased)**

```
Write pytest cases for parse_guess in logic_utils.py that try to break it:
think about what a real player could type into the box (empty, spaces,
words, typos, decimals, negative numbers, huge numbers, values just
outside the range). Each case should say what the game should do.
```

```
Some bugs live in app.py (New Game, attempts counter, switching difficulty),
not in pure functions. Write tests that drive app.py with Streamlit's
AppTest, then prove they catch the bugs by running them against the
original app.py from the first commit.
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Empty / whitespace-only (`None`, `""`, `"   "`) | 1st prompt | `test_empty_input_is_rejected` (parametrized) | ✅ | Pressing Submit with nothing typed, or a stray space, is the most common accidental input. It should ask for a guess, not crash or count a turn. |
| Non-numeric strings (`"abc"`, `"4O"` with a letter O, `"fifty"`, `"1e2x"`) | 1st prompt | `test_non_numeric_input_is_rejected` | ✅ | `"4O"` is a realistic typo that looks like a number. All of these must give "That is not a number." |
| Decimals (`"49.9"`, `"3.0"`, `"-0.5"`) | 1st prompt | `test_decimal_input_is_rejected_not_truncated` | ✅ (❌ on the original code) | The original `int(float(raw))` quietly turned 49.9 into 49, so the player got a hint for a number they never typed. |
| Negative, zero, above range, 20-digit number (`"-5"`, `"0"`, `"101"`, `"99999999999999999999"`) | 1st prompt | `test_out_of_range_input_is_rejected` | ✅ | These can never be the secret, so they shouldn't waste a guess. The huge number checks that Python's big ints don't cause a crash or overflow. |
| Exact bounds (`"1"`, `"100"`) | 1st prompt | `test_range_bounds_are_inclusive` | ✅ | The range check is easy to write off by one (`<` vs `<=`). 1 and 100 must be allowed. |
| Invalid input in the live app | 2nd prompt | `test_invalid_input_does_not_use_an_attempt` (AppTest) | ✅ (❌ on the original code) | The unit tests prove `parse_guess` rejects bad input, but only an app-level test proves `app.py` doesn't count the turn anyway. |

Full passing output is in the README's Test Results section and in `test_results.txt`.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

"Do all" the remaining challenges. For Challenge 2, the agent picked the rubric's **"Guess History" sidebar that visualizes how close previous guesses were**. It had to stay testable, not break any of the 48 existing tests, and keep hints hidden when "Show hint" is off.

**What did the agent do?**

| File | Change |
|------|--------|
| `logic_utils.py` | Added `get_closeness()` (0–1 score based on distance ÷ range size), `get_temperature()` (Hot / Warm / Cool / Cold bands in a `TEMPERATURE_BANDS` table), `build_round_record()` (one dict per guess) and `summarize_rounds()` (rows for the summary table), all with docstrings |
| `app.py` | Added `st.session_state.rounds`, reset in `start_new_game()`. Added `show_guess_history()`, which draws the sidebar: each guess with its Hot/Cold label and a `st.progress` "% close" bar. Each valid guess appends a record |
| `tests/test_game_logic.py` | 10 new unit tests: closeness at the extremes, symmetry, each temperature band, scaling with range, distinct colors, record/summary rows |
| `tests/test_app_flow.py` | 5 new AppTest tests: the sidebar lists each guess with its temperature and progress bar, hides closeness when hints are off, clears on New Game, the color-coded line appears, and the summary table shows only at game end |

Steps it took: wrote the pure functions first, then the UI, ran `pytest` (the 48 old tests still passed), added the new tests, ran `pycodestyle`/`pydocstyle`, then played a real game in the browser. Guesses 95 → 🧊 Cold 65% close, 63 → 🔥 Hot 97% close, 60 → win, and the summary table showed all three rows.

**What did you have to verify or fix manually?**

- **A wrong test.** The agent's first `test_temperature_scales_with_range` claimed 10 away on Hard (1–200) was "Hot". It's 10/199 = 5.03%, just over the 5% cutoff, so the test failed and the code was right. The test was changed to 8 away (4%). The Easy half of the test also used the wrong expected band ("Cool" instead of "Cold" for 42% off) and was corrected after printing the real value.
- **An old browser session.** A session opened before this change had no `rounds` key and would have crashed. The agent added `st.session_state.setdefault("rounds", [])`.
- **Dev server caching.** After the edit, the running Streamlit server showed `ImportError: cannot import name 'build_round_record'`. Streamlit re-runs `app.py` on save but keeps already-imported modules like `logic_utils` in memory. Restarting the server fixed it. That's not a bug in the code (pytest and a fresh `streamlit run` were fine), but it's easy to mistake for one.
- **Hint leak.** The closeness bars would reveal the answer even with "Show hint" unchecked, so the sidebar only shows guess numbers when hints are off (`test_guess_history_hides_closeness_when_hints_are_off`).

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Sub-task prompts (paraphrased):**

```
Add professional docstrings to every function in logic_utils.py
(Google style: summary, Args, Returns).
```

```
Review app.py, logic_utils.py, tests/ and scripts/ for PEP 8 compliance.
Run pycodestyle with default settings and pydocstyle on logic_utils.py,
fix what it reports, and save before/after output to lint_report.txt.
```

**Linting output before:** (full output in [`lint_report.txt`](lint_report.txt))

```
$ pycodestyle app.py logic_utils.py tests/ scripts/
app.py:23:80: E501 line too long (80 > 79 characters)
logic_utils.py:30:80: E501 line too long (81 > 79 characters)
logic_utils.py:44:80: E501 line too long (81 > 79 characters)
logic_utils.py:126:80: E501 line too long (81 > 79 characters)
logic_utils.py:127:80: E501 line too long (86 > 79 characters)
tests/test_game_logic.py:21:1: E302 expected 2 blank lines, found 1
... (16 x E302 in tests/test_game_logic.py)
scripts/reproduce_bugs.py:102:80: E501 line too long (113 > 79 characters)
$ pydocstyle --convention=google logic_utils.py
(no issues)
```

**Linting output after:**

```
$ pycodestyle app.py logic_utils.py tests/ scripts/
(no issues)
$ pydocstyle --convention=google logic_utils.py
(no issues)
```

**Changes applied:**

- **Docstrings:** every function in `logic_utils.py` (`get_range_for_difficulty`, `get_attempt_limit`, `parse_guess`, `check_guess`, `update_score`, `_settings_for`) has a docstring. The public ones have `Args:` / `Returns:` sections, and there's a module docstring too. `pydocstyle --convention=google` passes.
- **E302 (blank lines):** added the second blank line between the test functions in `tests/test_game_logic.py`. The starter tests used one, and new tests had copied that style.
- **E501 (line length):**
  - The two identical `DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Normal"])` lines were too long. Rather than just wrapping them, they were pulled into one `_settings_for()` helper with a `DEFAULT_DIFFICULTY` constant, which fixes the line length *and* removes the duplication.
  - Renamed `POINTS_LOST_PER_EXTRA_ATTEMPT` to `POINTS_PER_EXTRA_ATTEMPT` and added an `extra_attempts` variable, so the win formula fits on one line.
  - Split long assertions in tests into a named `expected` / `normal` / `levels` variable, and wrapped long `print` and f-string lines in `scripts/reproduce_bugs.py`.
- **Not changed:** the original starter only had 2 PEP 8 issues (E302/E305 around functions in `app.py`), and those went away with the refactor. The emoji in the hint strings were kept, since they're part of the game's UI and PEP 8 doesn't forbid them.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

The same prompt went to **Claude Sonnet 5.5** and **Claude Haiku 4.5**, each in a fresh session with no access to the repo (full prompt in [`model_comparison/prompt.md`](model_comparison/prompt.md)). It included the original `check_guess` and the `attempts % 2 == 0` → `str(secret)` snippet from `app.py`, plus the bug report: *9 vs a secret of 50 is "Too Low" on one attempt and "Too High" on the next, and 80 vs 47 shows "Go HIGHER!"*. Each model had to explain the root cause for a beginner and give fixed code. Both answers are saved word for word in [`model_comparison/claude_sonnet_5_5.md`](model_comparison/claude_sonnet_5_5.md) and [`model_comparison/claude_haiku_4_5.md`](model_comparison/claude_haiku_4_5.md).

To compare the fixes on behavior and not just looks, each `check_guess` was run on the same inputs:

| Input `(guess, secret)` | Sonnet 5.5 | Haiku 4.5 | Final version in `logic_utils.py` |
|---|---|---|---|
| `(9, 50)` | Too Low ✅ | Too Low ✅ | Too Low ✅ |
| `(80, 47)` | Too High, "Go LOWER" ✅ | Too High, "Go LOWER" ✅ | Too High, "Go LOWER" ✅ |
| `(50, 50)` | Win ✅ | Win ✅ | Win ✅ |
| `(9, "50")` (string secret) | Too Low (silently casts) | Too Low (silently casts) | `TypeError` (fails loudly) |
| `(50.7, 50)` | **Win** ❌ (`int(50.7)` = 50) | **Win** ❌ | Too High |
| `("abc", 50)` | `ValueError` | `"Invalid"` outcome | `TypeError` |

| | Model A | Model B |
|-|---------|---------|
| **Model name** | Claude Sonnet 5.5 | Claude Haiku 4.5 |
| **Response summary** | Two independent bugs: (1) `str(secret)` on even attempts, which triggers the `TypeError` fallback and an alphabetical `"9" > "50"` comparison; (2) swapped messages. Fix: cast both values with `int()` inside `check_guess`, drop the try/except, and pass `st.session_state.secret` straight in. | Three bugs: alternating secret type, the string-comparison fallback, and backwards messages. Fix: wrap `int(guess)` in try/except that returns a new `"Invalid"` outcome, cast the secret with `int()`, and stop alternating in `app.py`. |
| **More Pythonic?** | **Yes.** It's 7 lines with no exception handling, reads top to bottom, and keeps the function's contract (`Win` / `Too High` / `Too Low`). The `int()` casts are unnecessary here, since `app.py` always passes ints. | Less so. The try/except adds a fourth outcome, `"Invalid"`, that nothing in `app.py` or `update_score` handles, so an invalid guess would still use up an attempt. Input validation belongs in `parse_guess`, which already exists. |
| **Clearer explanation?** | **Yes.** It explains *why* 80 vs 47 is wrong even without the type bug ("a clean int comparison … still displays the wrong hint"), which ties each symptom in the report to a specific bug. | Clear and short, and it gives the ASCII reason for `"9" > "50"`. It calls the alternation "intentional in the code", which is confusing, and it doesn't link the 80 vs 47 symptom to the message bug. |

**Which did you prefer and why?**

**Sonnet 5.5.** It found the same root causes as Haiku, but its fix is smaller, doesn't invent an outcome the rest of the game can't handle, and its explanation maps each symptom to its cause. Neither fix was used as written, though. Both hide type problems with `int()` casts, and running them showed that 50.7 vs 50 counts as a **win**, which is the same silent-truncation problem as bug 7 in `parse_guess`. The version kept in `logic_utils.py` takes Sonnet's structure but drops the casts. `parse_guess` is the only place input gets converted, so `check_guess` can assume ints and fails loudly (`TypeError`) if a string ever slips through again, instead of quietly giving a wrong answer.
