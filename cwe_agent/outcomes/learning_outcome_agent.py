from pydantic import BaseModel
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

class LearningOutcome(BaseModel):
    cwe_id: str
    summary: str
    multiple_choice: str
    open_ended: str

generator = Agent(
    role="Learning Outcome Agent",
    goal="Design educational assessment for a secure coding vulnerability",
    backstory=(
        "You are a computer science educator tasked with helping students understand software vulnerabilities. "
        "Given an original and CWE-injected version of code, your job is to explain the issue and generate meaningful "
        "assessment questions to help the student learn."
        "Your response must be in JSON format:\n"
        "{\n"
        "  \"cwe_id\": \"<CWE-XXX>\",\n"
        "  \"summary\": \"<Full CWE summary explaining what they can learn from this CWE>\",\n"
        "  \"multiple_choice\": \"<difficult multiple choice question (with four answer options, one correct)>\",\n"
        "  \"open_ended\": \"<hard open-ended question>\"\n"
        "}"
    ),
    allow_delegation=False,
    # verbose=True,
    llm=llm,
)

def get_learning_outcome_task(
    original_code: str,
    injected_code: str,
    cwe_id: str,
    cwe_title: str,
    rationale: str,
    course_context: str,
    assignment_context: str
) -> Task:
    prompt = f"""
You are designing a learning outcome for a student in the course below.

Course:
{course_context}

Assignment:
{assignment_context}

The CWE being taught is:
- CWE ID: {cwe_id}
- Title: {cwe_title}

Below is the student's original code:
```
{original_code}
```

Below is the same code with a vulnerability introduced:
```
{injected_code}
```

Explanation for why this CWE was chosen: {rationale}

Your job is to generate an educational outcome for this student. Provide:

- A brief summary explaining what they can learn from this CWE
- A difficult multiple choice question (with four answer options, one correct)
- A hard open-ended question
Format your response in this JSON structure:
{{
    "cwe_id": "{cwe_id}",
    "summary": "...",
    "multiple_choice": "...",
    "open_ended": "..."
}}"""
    return Task( description=prompt, agent=generator, expected_output="JSON with summary, MCQ, and open-ended question", output_pydantic=LearningOutcome )
