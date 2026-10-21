# AceMock - Product Spec

## One-liner
A live AI mock-interview platform that grades you against a calibrated mentor rubric on real, company-specific questions. Not a resume tool, not a passive question database.

## Why it exists (the wedge)
The Pathwise knowledge base holds two assets competitors lack:
1. Real OA + interview questions for 100+ companies across SWE, Data, and Quant.
2. A mentor answer key: scoring rubrics with weighted criteria and a hint ladder.

Static banks do not convert to recurring revenue. Wrapping them in a graded practice loop does.

## Surfaces
### 1. Mock Agent (flagship)
- User picks a company, track (swe/data/quant), and round (coding/system-design/behavioral/oa).
- A live AI interviewer presents a real seeded question and runs the interview, dispensing the rubric's hint ladder one rung at a time when the candidate stalls.
- On finish, the grader scores the transcript against the rubric and returns a scorecard: weighted overall (1-5), hire recommendation, per-criterion justification, strengths, and improvements.
- Differentiator: the score is a calibrated answer key, not a generic LLM opinion. Hints used lower the relevant scores.

### 2. Behavioral Engine (module)
- User enters a raw STAR story; the engine maps it to the target company's values / leadership principles with evidence.
- User drills a probed value; the grader scores structure and specificity separately, flags vague "we" language and missing metrics, and returns the follow-ups a real interviewer would ask.
- Differentiator: behavioral is where strong coders fail; almost no tool grades it rigorously.

### 3. QuantReady (vertical)
- Brainteaser, probability, mental-math, and market-making drills with firm-specific tracks (Jane Street, Optiver, Citadel, SIG, IMC, HRT, DRW, Two Sigma).
- Numeric answers are checked deterministically; reasoning answers are graded by the model for partial credit.
- Differentiator: the highest willingness-to-pay audience, served by a modern product instead of PDFs.

## User stories (MVP)
- Browse companies and their question counts.
- Start a mock, converse turn by turn, finish, and receive a rubric scorecard.
- Build a STAR story, see value mapping, and grade a behavioral answer.
- Drill quant items by firm and category; get immediate correctness feedback.

## Monetization
- Free: limited mocks/month, browse banks, basic quant drills.
- Pro: unlimited mocks, full scorecards with per-criterion deep dive, solutions, all firm tracks, voice mode.
- QuantReady priced as a separate premium tier (the audience pays).

## Non-functional
- Server-enforced Pro gating; never leak solutions for locked content through the API.
- Stripe webhook idempotency for entitlement grants.
- Every external LLM call wrapped with retry + timeout; offline stub keeps the app runnable without keys.

## Out of scope (owned elsewhere)
- Resume generation and tailoring (HireReady).
- A crowdsourced/crawled question marketplace (Interview-DB idea).
