import os
from pydantic import BaseModel
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class CWEEvaluation(BaseModel):
    cwe_id: str
    relevance: int
    appropriateness: int
    naturalness: int
    pedagogical_value: int
    total_score: int
    evaluator_notes: str

load_dotenv()

# === Set up LLM ===
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY"),
)

evaluator = Agent(
    role="CWE Evaluator Agent",
    goal="Score the educational quality of a CWE-injected code variant",
    backstory=(
        "You are an educational security research expert. Your job is to evaluate CWE injections based on their learning value "
        "for students in a university-level secure software engineering course. You score CWE examples using defined criteria "
        "for research reproducibility."
        "Your response must be in JSON format:\n"
        "{\n"
        "  \"cwe_id\": \"<CWE-XXX>\",\n"
        "  \"cwe_title\": \"<Full CWE title>\",\n"
        "  \"relevance\": \"<1-10>\",\n"
        "  \"appropriateness\": \"<1-10>\",\n"
        "  \"naturalness\": \"<1-10>\",\n"
        "  \"pedagogical_value\": \"<1-10>\",\n"
        "  \"total_score\": \"<sum>\",\n"
        "  \"evaluator_notes\": \"<brief reasoning>\"\n"
        "}"
    ),
    allow_delegation=False,
    # verbose=True,
    llm=llm,
)

def get_evaluation_task(original_code, injected_code, cwe_info, course_context, assignment_context, diff_score, language_name):
    return Task(
        description=f"""
Evaluate the following CWE-injected student code.

Course:
{course_context}

Assignment:
{assignment_context}

CWE to inject:
- CWE ID: {cwe_info['cwe_id']}
- Title: {cwe_info['cwe_title']}
- Description: {cwe_info['cwe_description']}

Original code:
```{language_name}
{original_code}
```

Injected code:
```{language_name}
{injected_code}
```

Difference from original code (Levenshtein similarity): {diff_score:.2f}%

Evaluate this code variant using the following criteria, scoring each from 1-10:
1. Relevance — Does the CWE logically apply to this assignment?
2. Appropriateness — Is the CWE appropriate for the course/assignment level?
3. Naturalness — Does the CWE fit in the code without changing its original logic or structure significantly?
4. Pedagogical Value — Will this help a student learn secure coding?

Respond in this exact format:
{{
  "cwe_id": "{cwe_info['cwe_id']}",
  "cwe_title: "{cwe_info['cwe_title']}",
  "relevance": <1-10>,
  "appropriateness": <1-10>,
  "naturalness": <1-10>,
  "pedagogical_value": <1-10>,
  "total_score": <sum>,
  "evaluator_notes": "<brief reasoning>"
}}
        """,
        agent=evaluator,
        expected_output="Structured JSON with scoring and justification",
        output_pydantic=CWEEvaluation
    )