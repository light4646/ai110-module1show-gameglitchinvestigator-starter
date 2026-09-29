"""Drive app.py headlessly with Streamlit's AppTest and print what the player sees.

Usage: python scripts/reproduce_bugs.py > bug_trace_before.txt
The secret is pinned through session_state so every run is reproducible.
"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

# Let app.py import logic_utils when this script is run from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def new_app(secret, difficulty="Normal"):
    at = AppTest.from_file("app.py")
    at.run()
    if difficulty != "Normal":
        at.selectbox[0].select(difficulty)
        at.run()
    at.session_state["secret"] = secret
    return at


def screen(at):
    lines = []
    for kind in ("info", "warning", "success", "error"):
        for el in getattr(at, kind):
            lines.append(f"    [{kind}] {el.value}")
    lines.append(
        f"    state: attempts={at.session_state['attempts']} "
        f"score={at.session_state['score']} status={at.session_state['status']} "
        f"secret={at.session_state['secret']}"
    )
    return "\n".join(lines)


def guess(at, value):
    at.text_input[0].input(str(value))
    at.button[0].click()
    at.run()
    return at


def button(at, label_start):
    for b in at.button:
        if b.label.startswith(label_start):
            b.click()
            at.run()
            return at
    raise ValueError(label_start)


def scenario(title):
    print(f"\n=== {title} ===")


scenario("A. Hints point the wrong way (secret=50, Normal)")
at = new_app(50)
print("  start:")
print(screen(at))
print("  guess 60:")
print(screen(guess(at, 60)))

scenario("B. Even-numbered attempts compare against a string (secret=50)")
at = new_app(50)
print("  guess 40 (attempt #2 internally):")
print(screen(guess(at, 40)))
print("  guess 9 (attempt #3):")
print(screen(guess(at, 9)))
print("  guess 9 again (attempt #4):")
print(screen(guess(at, 9)))

scenario("C. Attempt counter starts at 1 (Normal allows 8)")
at = new_app(50)
print("  before any guess:")
print(screen(at))
for g in (10, 20, 30, 40, 45, 46, 47):
    guess(at, g)
print("  after 7 wrong guesses:")
print(screen(at))

scenario("D. New Game after a win does not restart the game")
at = new_app(50)
guess(at, 50)
print("  after winning guess 50:")
print(screen(at))
button(at, "New Game")
print("  after clicking New Game:")
print(screen(at))

scenario("E. Difficulty ranges are wrong and switching keeps an out-of-range secret")
at = new_app(80)
at.selectbox[0].select("Easy")
at.run()
print("  Normal game (secret=80), then switch to Easy:")
print("  Easy sidebar says:", [c.value for c in at.sidebar.caption])
print(screen(at))
at = new_app(3, difficulty="Hard")
print("  Hard sidebar says:", [c.value for c in at.sidebar.caption])
button(at, "New Game")
print("  Hard -> New Game, new secret:", at.session_state["secret"], "(should be inside the Hard sidebar range)")

scenario("F. Score rewards some wrong guesses (secret=50)")
at = new_app(50)
guess(at, 70)
print("  guess 70 (Too High, attempt #2):")
print(screen(at))

scenario("G. Invalid input still burns an attempt; decimals are truncated")
at = new_app(50)
guess(at, "abc")
print("  guess 'abc':")
print(screen(at))
guess(at, "49.9")
print("  guess '49.9':")
print(screen(at))
print("    history:", at.session_state["history"])
