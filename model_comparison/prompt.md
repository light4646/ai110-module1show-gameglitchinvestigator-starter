# Prompt given to both models (identical, fresh session, no repo access)

> You are helping a student debug an AI-generated Streamlit number-guessing game. Do NOT use any tools, do not read or edit files. Just answer in text.
>
> *(original buggy `check_guess` from app.py and the `attempts % 2 == 0` / `str(secret)` snippet from the submit handler were pasted here)*
>
> Bug report: with the secret at 50, guessing 9 gives a "Too Low" outcome on one attempt, but guessing 9 again on the next attempt gives a "Too High" outcome (and the score changes accordingly). Also, a guess of 80 vs a secret of 47 displays "Go HIGHER!".
>
> Please: 1) explain the root cause(s) in plain language a beginner could follow, 2) give your fixed version of the code (both check_guess and the app.py snippet). Keep the answer under 350 words.
