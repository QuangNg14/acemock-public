# Seeding Guide

The data moat is real, company-specific questions plus mentor rubrics. Seed in this order.

## 0. Schema
```bash
cd backend
alembic upgrade head      # production path
# or, for a quick throwaway DB:
python scripts/init_db.py
```

## 1. Rubrics (required for grading)
```bash
python scripts/seed_rubrics.py
```
Seeds the SWE coding, system-design, and behavioral rubrics with weighted criteria, anchored 1/3/5 levels, and a hint ladder. The grader will not run without a matching rubric for the session's track + round.

## 2. Question banks (from the Pathwise vault)
```bash
python scripts/seed_vault.py --vault "/path/to/your-vault" --limit 300
```
Reads:
- `Pathwise Resources/03-Online-Assessments/All Shared Online Assessments (OA)/` -> OA-round questions
- `Pathwise Resources/06-Company-Interviews/` -> interview-round questions

For each note it derives:
- **company** from the filename (strips OA/Interview/date suffixes),
- **track** (quant for known firms or quant/trading keywords; data for DS/DE/DA/ML; else swe),
- **round** (oa / system_design / behavioral / phone / onsite).

Dedup is by source file path, so re-running is safe.

## 3. Quant drills
```bash
python scripts/seed_quant.py
```
Seeds a starter set across all categories and firm tracks. Extend `DRILLS` from the vault's quant interview notes over time.

## 4. Embeddings (optional, enables semantic retrieval)
Set `OPENAI_API_KEY` and `EMBEDDING_MODEL`; a future `backfill_embeddings.py` populates `Question.embedding`. The IVFFlat cosine index already exists from the baseline migration.

## Verify
```bash
uvicorn app.main:app --reload
# then:
curl http://localhost:8000/questions/companies
curl -X POST http://localhost:8000/mock/start -H "Content-Type: application/json" \
  -d '{"company":"Amazon","track":"swe","round":"coding"}'
```

## Notes
- Without an LLM key the app uses a deterministic offline stub, so the full start -> message -> grade loop still works for development and CI.
- Never commit real keys. Use `.env` (gitignored).
