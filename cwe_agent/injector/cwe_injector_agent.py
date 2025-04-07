import os
import csv
from pathlib import Path
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader
from pydantic import BaseModel

from cwe_agent.helpers.io_utils import extract_text_from_pdf, load_student_code


class CWEInjectionOutput(BaseModel):
    cwe_id: str
    cwe_title: str
    modified_code: str
    injection_notes: str

load_dotenv()

# === Set up LLM ===
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# === Load CWE from CSV ===
def load_cwe_by_id(cwe_id):
    with open(Path(os.path.join(PROJECT_ROOT, 'data', CWE_CSV_FILENAME)), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["CWE-ID"] == str(cwe_id):
                return {
                    "cwe_id": row["CWE-ID"],
                    "cwe_title": row["Name"],
                    "cwe_description": row["Description"]
                }
    raise ValueError(f"CWE {cwe_id} not found in {CWE_CSV_FILENAME}")


# === CWE Injector Agent ===
injector = Agent(
    role="CWE Injector Agent",
    goal="Inject a specific CWE vulnerability into student code while preserving structure and context.",
    backstory=(
        "You are a secure coding assistant that simulates real-world vulnerabilities to help students learn.\n\n"
        "You are tasked with injecting a specific CWE vulnerability into student code. Your goal is to preserve the original structure and learning objectives of the student's code while introducing the vulnerability in a realistic and educational way. You should NOT explain anything—only return the modified code and metadata.\n\n"
        "You may change or add imports and helper functions if needed, but do NOT rewrite or drastically restructure the student's code. Do not include comments unless they were already present. Your changes should be minimally invasive unless the CWE requires structural shifts.\n\n"
        "Your response must be in JSON format:\n"
        "{\n"
        "  \"cwe_id\": \"<CWE-XXX>\",\n"
        "  \"cwe_title\": \"<Full CWE title>\",\n"
        "  \"modified_code\": \"<code with vulnerability injected>\",\n"
        "  \"injection_notes\": \"<brief description of where and how the vulnerability was introduced>\"\n"
        "}"
    ),
    allow_delegation=False,
    # verbose=True,
    llm=llm,
)

# === Define a CWE Injection Task ===
def get_injection_task(student_code, course_text, assignment_text, cwe_info, language_name):
    prompt = f"""You are given a student's {language_name} code written for a university assignment.

Course:
{course_text}

Assignment:
{assignment_text}

CWE to inject:
- CWE ID: {cwe_info['cwe_id']}
- Title: {cwe_info['cwe_title']}
- Description: {cwe_info['cwe_description']}

Student code:
```{language_name}
{student_code}
```

Your job is to inject the above CWE into the student code in a way that is realistic, educational, and minimally disruptive to the original code's intention.

Return your output in this JSON format:
{{
    "cwe_id": "{cwe_info['cwe_id']}",
    "cwe_title": "{cwe_info['cwe_title']}",
    "modified_code": "<code with vulnerability injected>",
    "injection_notes": "<brief description of where and how the vulnerability was introduced>"
}}""" 

    return Task( description=prompt.strip(), agent=injector, expected_output="JSON with modified code and injection notes", output_pydantic=CWEInjectionOutput)

# === Language Inference Helper ===
def infer_language_from_extension(filepath): 
    ext = Path(filepath).suffix.lower()
    return { ".py": "python", ".js": "javascript", ".java": "java", ".cpp": "cpp", ".c": "c", ".ts": "typescript", ".rb": "ruby", ".php": "php", ".go": "go" }.get(ext, "plaintext")


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent
    CWE_CSV_FILENAME = 'cwe.csv'
    COURSE_PDF_FILENAME = "course-context.pdf"
    ASSIGNMENT_PDF_FILENAME = 'a2-rest.pdf'
    STUDENT_CODE_FILENAME = "student_code2.py"  # Can be any language
    
    # === Load all inputs ===
    course_text = extract_text_from_pdf(COURSE_PDF_FILENAME)
    assignment_text = extract_text_from_pdf(ASSIGNMENT_PDF_FILENAME)
    student_code = load_student_code(STUDENT_CODE_FILENAME)
    language_name = infer_language_from_extension(STUDENT_CODE_FILENAME)
    cwe_info = load_cwe_by_id("798") # Change this to loop through all CWEs later

    # === Create and run Crew ===
    task = get_injection_task(student_code, course_text, assignment_text, cwe_info, language_name)
    crew = Crew(agents=[injector], tasks=[task], verbose=True)

    # === Execute the CWE injection ===
    result = crew.kickoff() 
    print("\n=== CWE Injection Result ===\n") 
    print(result)