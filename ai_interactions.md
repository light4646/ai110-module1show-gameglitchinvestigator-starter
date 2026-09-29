# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

AI tool used for everything below: **Claude Code (Claude Opus 5.5), agent mode**, in the Claude desktop app.

The actual prompt I gave the agent was *"okay now fully do proj one"*, with the course rubric saved as a checklist. The "prompts" below are the sub-tasks the agent broke that into (paraphrased), so it's clear what each step was asked to do.

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
