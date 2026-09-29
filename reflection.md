# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**What did the game look like the first time you ran it?** It loaded without crashing and looked normal, with a title, an "Attempts left" box, a guess box and Submit / New Game buttons. The problems only showed up once I started guessing with the Developer Debug Info open. Even before my first guess, the box said "Attempts left: 7" on Normal, which is supposed to allow 8.

**What concrete bugs did you notice at the start?** With the secret at 47, I guessed 80 and the game told me "📈 Go HIGHER!", so the hints were backwards. After I won, clicking "New Game 🔁" didn't restart anything, and the screen kept saying "You already won." The debug panel also still showed `Attempts: 1` and `History: []` right after a guess, because it was drawn before the guess was processed.

To make each bug reproducible, I pinned the secret with `st.session_state` and drove the app with Streamlit's `AppTest` (`scripts/reproduce_bugs.py`). The full output is in [`bug_trace_before.txt`](bug_trace_before.txt).

**Bugs found (expected vs actual, with the code-level cause):**

1. **Hints point the wrong way.** *Expected:* a guess above the secret says "Go LOWER". *Actual:* 80 vs 47 (and 60 vs 50) says "📈 Go HIGHER!". *Cause:* in `check_guess` the messages are swapped: the `guess > secret` branch returns "Go HIGHER!" and the else branch returns "Go LOWER!".
2. **Every other guess is compared as text, not as a number.** *Expected:* 9 vs 50 is always "Too Low". *Actual:* on attempt #3 it's "Too Low", but on attempt #4 the same guess is "Too High". *Cause:* in `app.py`, `if st.session_state.attempts % 2 == 0: secret = str(st.session_state.secret)`. `int > str` raises `TypeError`, and the `except TypeError` fallback in `check_guess` compares `"9" > "50"` alphabetically, which is `True`. (The swapped message from bug 1 happens to make that hint *look* right, but the outcome and score are wrong.)
3. **You get one fewer guess than the difficulty allows.** *Expected:* Normal gives 8 guesses and the box says "Attempts left: 8". *Actual:* it starts at 7, and the game ends "Out of attempts!" after only 7 guesses. *Cause:* `st.session_state.attempts = 1` on the first load (New Game resets it to 0, so the two paths disagree). The info box also renders *before* the submit logic runs, so it always shows the previous turn's count.
4. **New Game doesn't start a new game after a win or loss.** *Expected:* after winning, New Game resets and lets you play. *Actual:* the secret changes but the screen says "You already won. Start a new game to play again.", and score stays 70. *Cause:* the `new_game` block resets `attempts` and `secret` but never `status`, `score` or `history`, and the `status != "playing"` check then calls `st.stop()`.
5. **Difficulty ranges are wrong.** *Expected:* Hard is harder than Normal, and New Game and the secret follow the chosen range. *Actual:* Hard is 1–50 (easier than Normal's 1–100). New Game on Hard produced secrets like 84 and 92. Switching Normal → Easy kept secret 80 even though Easy is 1–20, and the prompt always says "between 1 and 100". *Cause:* `get_range_for_difficulty` returns `1, 50` for Hard, `new_game` uses `random.randint(1, 100)`, the secret is only created once, and the info text is hard-coded.
6. **Score rewards wrong guesses and undervalues wins.** *Expected:* wrong guesses never add points, and a first-try win gets the most points. *Actual:* guess 70 vs 50 (Too High on attempt #2) gave **+5**, and a first-guess win scored only 70. *Cause:* in `update_score`, `"Too High"` adds 5 when `attempt_number % 2 == 0`, and the win formula uses `attempt_number + 1`, which is an off-by-one on top of attempts starting at 1.
7. **Invalid input still costs an attempt, and decimals are truncated.** *Expected:* "abc" shows an error without using a turn, and "49.9" is rejected. *Actual:* "abc" dropped attempts left from 7 to 6, and "49.9" was silently treated as 49. *Cause:* `attempts += 1` runs before `parse_guess`, and `parse_guess` does `int(float(raw))`.

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret 47, guess **80** (live in browser) | "Too High" / "Go LOWER" | "📈 Go HIGHER!" | none (no crash) |
| Secret 50, guess **9** on attempt #3, then **9** again on attempt #4 | "Too Low" both times | Attempt #3: "Too Low". Attempt #4: outcome "Too High", score +5 | none. The `TypeError` from `int > str` is caught silently |
| Fresh Normal game, no guess yet | "Attempts left: 8" | "Attempts left: 7". Lost after 7 guesses: "Out of attempts! … Score: -35" | none |
| Win with **50**, then click **New Game** | Fresh game, status playing, score 0 | "You already won. Start a new game to play again.", status=won, score=70 | none |
| Difficulty **Hard**, click **New Game** | Secret in 1–50 | Secrets 84, 92, 74, 60 | none |
| Secret 50, guess **70** on attempt #2 | Score goes down (wrong guess) | Score **+5** (0 → 5) | none |
| Guess **abc** | Error, no attempt used | "That is not a number." and attempts left 7 → 6 | none |
| Guess **49.9** | Rejected as not a whole number | Treated as 49, "Go LOWER!" | none |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

**Which AI tools did you use?** I used Claude Code (Claude Opus 5.5) in agent mode inside the Claude desktop app. It read the repo, ran and played the game, edited `app.py` and `logic_utils.py`, and wrote the pytest tests. For the model comparison stretch challenge, I also gave one bug to Claude Sonnet 5.5 and Claude Haiku 4.5.

**One AI suggestion that was correct:** Claude explained that on even attempts `app.py` turns the secret into a string, so `check_guess` falls back to comparing text, and `"9" > "50"` is `True`. It suggested removing both the `str()` conversion and the `except TypeError` fallback, so the comparison is always int vs int. I verified it with `test_single_digit_guess_is_compared_numerically`, plus an app-flow test that fails on the original code and passes on the fix.

**One AI suggestion I did not accept as written:** The AI-written starter tests compared `check_guess(60, 50)` to `"Too High"`, but the function returns a tuple `(outcome, message)`, so the tests could never pass. Instead of changing `check_guess` to return a bare string (which `app.py` can't use, because it needs the message too), I changed the tests to unpack the tuple. I also rejected the README's claim that the secret resets on every Submit, because the debug panel showed it stayed the same, so we fixed the real state bug in New Game instead.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

**How did you decide whether a bug was really fixed?** A bug only counted as fixed if a test for it passed, the same test failed on the original code, and the game behaved correctly when played. Checking against the original code mattered, because one of the AI's tests passed on the broken version when two bugs cancelled each other out. We rewrote that test, and now all 9 app-flow tests fail on the original `app.py` and pass on the fixed one.

**Describe at least one test you ran and what it showed.** `test_new_game_after_win_really_restarts` wins with 50, clicks New Game and checks that `status`, `score`, `attempts` and `history` are all reset. On the original code it failed with `status == "won"`, which is exactly the "You already won" bug I saw in the game. I also played the fixed game manually (secret 55): 80 said "Go LOWER", 40 said "Go HIGHER", 55 won with a score of 70, and New Game reset everything.

**Did AI help you design or understand any tests? How?** Yes, Claude designed most of the tests, including the Streamlit `AppTest` tests that click buttons in the app without a browser. The most useful idea was to test the symptom I actually saw, like 9 vs 50 flipping between guesses, not just the easy happy-path case. It also suggested running the new tests against the old code to prove they catch the bugs.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

A Streamlit app is a Python script that runs again from top to bottom every time you click a button or type something, and each of those runs is called a "rerun". Normal variables get rebuilt on every rerun, so anything the game needs to remember, like the secret, score and attempts, has to live in `st.session_state`, which survives reruns. This project showed me that order matters, because anything drawn above the Submit code shows last turn's values, and that any state you forget to reset, like `status` after a win, just stays there.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

**One habit to reuse:** I want to keep running new tests against the old, broken code, not just the fixed code. A test that passes on buggy code isn't testing anything, and that check caught a weak test in this project. I also want to keep committing after each phase, so the Git history tells the story of the work.

**One thing to do differently:** Next time I'd check the AI's claims against the running program sooner, because the README's hint about the secret resetting was wrong. I'd also give the AI one bug at a time, so each change is small enough for me to review properly. And I'd play the game myself before letting the agent do the whole project, so I understand what I'm fixing.

**How this project changed your thinking about AI-generated code:** AI code can look finished and still be wrong in ways that only show up when you actually use it, like hints pointing the wrong way or two bugs hiding each other. That goes for AI-written tests and docs too, not just the code. Now I treat AI output as a draft that I have to verify with real inputs and tests before I trust it.
