# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran `python -m streamlit run app.py`, the game loaded without crashing and looked normal: a title, a blue "Guess a number between 1 and 100. Attempts left: 7" box, a guess box and Submit / New Game buttons. It fell apart as soon as I played. With the Developer Debug Info open (secret = 47), I guessed 80 and the game told me "📈 Go HIGHER!", which is backwards. The debug panel still said `Attempts: 1` and `History: []` after my guess, and the "Attempts left" number was already wrong before I guessed anything (7 on Normal, which allows 8). After I won a game, clicking "New Game 🔁" didn't restart anything. It just kept saying "You already won."

To make each bug reproducible, I pinned the secret with `st.session_state` and drove the app with Streamlit's `AppTest` (`scripts/reproduce_bugs.py`). The full output is committed in [`bug_trace_before.txt`](bug_trace_before.txt).

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

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
