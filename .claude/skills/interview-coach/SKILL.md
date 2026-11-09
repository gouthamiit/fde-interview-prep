---
name: interview-coach
description: Run a mock Forward Deployed Engineer (FDE) interview round in chat — ask which round, present one question from data/questions.json, take the user's answer, then score it 0-5 on each rubric category (total /20) with one concrete improvement. Load this whenever the user asks to "practise", "practice", "run a mock round", "mock interview", "quiz me", or wants an answer scored against the rubric.
---

# Interview Coach — one mock FDE round

Runs a single mock interview round in the conversation. The question bank and
rubric already live in this repo, so read them fresh each time rather than
relying on memory — they are the source of truth.

## Steps

1. **Ask which round.** Read `data/questions.json` and list the distinct
   `round` values (currently: decomposition, behavioral, system-design,
   client-roleplay). Ask the user to pick one. If they already named a round,
   skip this step.

2. **Present one question.** Pick one question from that round (random, or the
   next one they haven't done this session). Show its `id` and `prompt`
   verbatim, then stop and wait for the answer. Do not hint, coach, or
   pre-empt the answer.

3. **Take the answer.** Wait for the user's full reply. If it is a one-liner,
   ask once whether that's their final answer before scoring.

4. **Score it.** Read `data/rubric.md` and score the answer **0–5** on each of
   its categories (they mirror `scoring.RUBRIC_CATEGORIES`):
   - Clarifying questions
   - Decomposition
   - Risk identification
   - Communication

   Use the rubric's score guide: 0 = absent · 1–2 = weak · 3 = solid ·
   4 = strong · 5 = exceptional. Be honest — an average answer is a 3, not a 4.
   Base each score on what the user actually said, quoting a short phrase
   as evidence where you can.

5. **Report** in exactly this shape:

   ```
   Question: <id> — <prompt>

   | Category             | Score | Why                    |
   |----------------------|-------|------------------------|
   | Clarifying questions | x/5   | <one line of evidence> |
   | Decomposition        | x/5   | ...                    |
   | Risk identification  | x/5   | ...                    |
   | Communication        | x/5   | ...                    |
   | **Total**            | **N/20** |                     |

   One improvement: <the single highest-leverage change, phrased as
   something to do differently next time>
   ```

   Give **one** improvement only — the one that would raise the total most.

6. **Offer another round** and stop.

## Optional context

If the `interview-guides` MCP server is connected, you may fetch the matching
guide (`decomposition-guide`, `behavioral-star-guide`, `system-design-guide`)
to make the improvement tip more specific. Don't paste the guide to the user.

## Don'ts

- Don't write to `data/results.json` or any file — this skill is chat-only.
- Don't call the app's scoring endpoints or the OpenAI API; you are the scorer.
- If the rubric categories in `data/rubric.md` change, score against what the
  file says, not the list above.
