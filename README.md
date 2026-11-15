# Integration Factory Agent

**AI agents that learn unfamiliar hospital systems, map them to FHIR and write integration code, with a person approving every step.**

Team **Fourmula** · EXL × Trinity Data & AI Hackathon 2026 · **Challenge 01: Agentic healthcare integration**

- 🎥 **Demo video (2:39):** https://drive.google.com/file/d/1kby9WUzYwDVozacPVAupLvaIMnYeiTwv/view?usp=drive_link
- 👥 **Team:** Sreelakshmi Shimji Sreeja (team leader), Jewel Rose Binoy, Shravanthika Rajkumar, Rithanya Kumarasamy Senthilkumar

---

## The problem

A global healthcare client runs about 45 on-premise and cloud systems. Only about a quarter expose usable APIs, and even those need rework. That leaves 30+ integrations to hand-build in a 3–5 month window: slow, inconsistent and costly.

## What we built

A working prototype of an agentic "integration factory", proven on three deliberately different mock hospital systems built from synthetic Synthea data (150 patients):

| Mock system | How it provides data | Size |
|---|---|---|
| Patient registration | REST API (`GET /patients`), JSON, day-first dates | 150 patients |
| Hospital database | Legacy SQLite: `TBL_VISIT` + lookup `LKP_VISIT_TYPE`, cryptic columns | 878 visits |
| Laboratory system | Nightly CSV export, LOINC codes, values as text | 4,994 lab results |

Nine data problems were planted on purpose (missing patient IDs, "pending" results, records for unknown patients).

## How it works

The agent (Google Gemini) runs five stages. **Each stage is locked until a person approves it**, and every approval and note is written to an audit log.

1. **Discover**: the agent's tools open the API, database and file and profile each system. Personal fields are masked before anything reaches the AI. ✋ *Human approval*
2. **Design**: the agent chooses how to connect each system (REST API pull, SQL batch query, file ingest), maps every field to FHIR and writes an OpenAPI spec. ✋ *Human approval*
3. **Generate**: the agent writes each adapter from one shared template.
4. **Validate**: 15 automated checks per adapter (safety, FHIR structure, broken-data handling, no personal data in logs); failing code can be retried up to 3 times. ✋ *Human approval*
5. **Operate**: the adapters run behind one common FHIR API (Patient, Encounter, Observation), raising alerts for bad data.

## Results (reviewed live run, 14 Nov 2026)

| Measure | Result |
|---|---|
| Correctness | 16/16 key fields mapped correctly (against our answer key) |
| Consistency | 15/15 template rule checks (5 rules × 3 adapters) |
| Reliability | 42/42 automated tests, incl. deliberately broken records |
| Bad data caught | 9/9 (6 rows rejected and logged, 3 unknown-patient records held for review) |
| Records loaded | 6,016 (150 patients, 878 visits, 4,988 lab results) |
| Privacy | 0 personal values found in an automated scan of the logs |
| Time | ≈19 min end to end (3.9 min AI time + human review) vs a 53-min manual baseline* |

Human review in the live run caught one false alarm at Discover and two design gaps at Design; the agent fixed them from plain-English feedback.

\*The manual baseline code was written with Claude's help, then reviewed, run and timed by our team.

## Repository contents

| File(s) | What it is |
|---|---|
| `EXL_Agent_Prototype_v3.ipynb` | The agent notebook (Google Colab) |
| `patients.json`, `hospital.db`, `lab_results.csv` | The three mock systems (patient API data, legacy SQL database, lab CSV) |
| `field_descriptions.md`, `answer_key.json` | System owners' field notes (given to the agent) and the mapping answer key |
| `patient_api.py`, `hospital_db.py`, `lab_csv.py` | **The integration code the agent generated** in the reviewed live run |
| `discover.json`, `design.json`, `generate_*_attempt1.json` | The agent's saved Gemini answers from the live run (used by replay mode) |
| `1_discovery.json` … `5_results_comparison.csv` | Everything else the live run produced: discovery, mappings, OpenAPI spec, generation summary, suggested tests, alerts, combined patient record, results |
| `audit_log.jsonl` | Every AI call and human approval, with times and reviewer notes |
| `test_bad_lab.csv` | Deliberately broken lab rows used by the validation tests |
| `Fourmula_Challenge01_Submission.pdf`, `Fourmula_AI_Tools_Declaration.docx` | Submission slides and AI tools declaration |

## How to run it

1. Open `EXL_Agent_Prototype_v3.ipynb` in **Google Colab** (File → Upload notebook) and run cells 1 and 2 (they create the `team_data` and `outputs/agent_cache` folders).
2. In Colab's Files panel, upload `patients.json`, `hospital.db`, `lab_results.csv`, `field_descriptions.md` and `answer_key.json` into **`team_data/`**.
3. **Replay mode (no API key):** upload `discover.json`, `design.json` and the three `generate_*_attempt1.json` files into **`outputs/agent_cache/`**, and keep `MODE = replay`, `DATA_SOURCE = team` in cell 1.
   **Live mode:** add a Gemini API key in Colab Secrets as `GEMINI_API_KEY` and set `MODE = live`.
4. Run the cells in order. At each **✅ Human review** cell, read the output, type your name, tick **APPROVED** and run the cell to unlock the next stage.

Replay mode prints `replay · saved output from an earlier live run` so it is always clear when saved outputs are used.

## Responsible AI

- **Synthetic data only** (Synthea); no real patients.
- **Privacy:** personal fields masked before the AI sees them; logs hold only row numbers and field names; automated log scan.
- **Code safety:** generated code is checked before it runs (no network, no file writing, only approved imports).
- **Human control:** every stage locked until a person approves; bad records rejected and alerted, never guessed.

## Limitations and next steps

- Synthetic data; small sample (150 patients, 3 systems); local Colab prototype with one model.
- Tests and answer key written by our team; LOINC format not validated; self-healing built but not needed in this run.
- The Azure / .NET production design is a proposal, not built or deployed.
- Next: more and messier systems (e.g. HL7 v2 feeds), an independent test set and hand-built baseline, .NET adapters via the client's CI/CD on Azure, and the model hosted in Azure OpenAI in the client's tenant.

## AI tools used

Google Gemini (the agent's model). Claude (Anthropic) helped write the notebook code, build the mock systems, write the replay backup outputs and the manual baseline code, turn our slide plan into the deck and edit the demo video. See `Fourmula_AI_Tools_Declaration.docx`.
