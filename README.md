# CWE Educational Vulnerability Injection System

This project implements an end-to-end AI-based research pipeline for injecting, evaluating, ranking, and assessing CWE (Common Weakness Enumeration) vulnerabilities in student-submitted code to enhance secure coding education.

The system consists of 4 intelligent agents that process and assess student code submissions with contextual awareness of the course and assignment. It is intended for academic research and reproducible experimentation in security education.

---

## 📐 System Architecture Overview

### 🔁 Agent Flow

1. **Agent 1: CWE Injector**
   - Injects 2024 Top 25 CWEs into student code.
   - Attempts to minimally modify the structure and preserve educational relevance.
   - **Inputs**:
     - Student source code file
     - Course and assignment PDF context
     - CWE list (from CSV)
   - **Outputs**:
     - Modified student code with CWE injected
     - JSON file describing the injected CWE, injection notes, and code

2. **Agent 2: CWE Evaluator**
   - Evaluates each CWE-injected variant based on multiple educational criteria.
   - Performs a diff analysis against original code.
   - **Inputs**:
     - Original and modified code
     - Course and assignment context
     - Injection metadata (CWE ID, title, description)
   - **Scoring Criteria**:
     - Relevance (x3)
     - Pedagogical Value (x3)
     - Appropriateness (x2)
     - Naturalness (x1)
   - **Output**:
     - Structured score (JSON) per CWE injection per student

3. **Agent 3: CWE Ranker**
   - Ranks all CWE variants for a student based on weighted scores and rationale.
   - Uses LLM reasoning to resolve tie-breakers with course/assignment context.
   - **Inputs**:
     - All scored CWE JSONs for the student
     - Course and assignment context
   - **Output**:
     - Ranked CWE list
     - Top CWE selection
     - Justification rationale (JSON)

4. **Agent 4: Learning Outcome Generator**
   - Generates an educational feedback artifact for the top CWE.
   - Provides a concise summary, a multiple choice question, and an open-ended question.
   - **Inputs**:
     - Original + modified code
     - Top CWE ID, title, rationale
     - Course and assignment context
   - **Output**:
     - Learning artifact in structured JSON

---

## 🛠️ Installation Instructions

### Requirements
- Python 3.10+
- Poetry
- OpenAI API Key

### Environment Setup
```bash
git clone https://github.com/your-org/cwe-injector-research.git
cd cwe-injector-research
poetry install
```

### Add OpenAI API Key
Create a `.env` file at the root level:
```
OPENAI_API_KEY=sk-...
```

---

## 🚀 Running the Full Pipeline

This runs all 4 agents sequentially:
```bash
poetry run python cwe_agent/run_full_pipeline.py
```

### File Dependencies
Ensure the following exist in `/data`:
- `student_code2.py`
- `course-context.pdf`
- `a2-rest.pdf`
- `cwe.csv` (from MITRE Top 25 2024 page) - Downloadable - https://cwe.mitre.org/data/csv/1430.csv.zip

### Output Artifacts
- Injected variants: `research-artifacts/injected_cwes/{student_id}/`
- Evaluated scores: `research-artifacts/scored_cwes/{student_id}/`
- Ranked output: `final_ranked_cwe.json`
- Student learning outcome: `learning_outcome.json`

---

## 📊 Scoring Strategy (Agent 2)

### Core Scoring Dimensions
| Criterion         | Description                                                   | Weight |
|------------------|---------------------------------------------------------------|--------|
| Relevance        | Is the CWE relevant to the code and context?                 | 3      |
| Pedagogical Value| Will this CWE teach something meaningful?                    | 3      |
| Appropriateness  | Is it suitable for the student's level and course goals?     | 2      |
| Naturalness      | Does the injection minimally alter original code intent?     | 1      |

Final score = weighted sum of the above criteria.

### Tie-breaking
To resolve ties in CWE scores:
- We incorporate both LLM judgment (Agent 3)
- Use rationale from course and assignment context
- Future versions may add AST similarity metrics

---

## 📘 Research Considerations

- Agents operate based on reproducible, contextual information from PDF syllabi and assignment prompts.
- LLM scoring is deterministic when model and seed are held constant.
- Every step logs raw output to ensure transparency and auditability.
- Scoring and outcome generation can be further enhanced with Langfuse in the future.

---

## 🧩 Future Enhancements
- Use Langfuse to version and track all prompts/responses
- Visual dashboard of CWE injection coverage
- Instructor portal for injecting course-specific CWEs
- Research evaluation forms to assess student learning delta

---

## 🤝 Credits
Built in collaboration with academic researchers in secure software engineering. For use in educational research settings.
