from cwe_agent.injector.inject_and_store_cwes import inject_cwe_variants_for_student
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

inject_cwe_variants_for_student(
    project_root=PROJECT_ROOT,
    cwe_csv_file=os.path.join(PROJECT_ROOT, "data", "cwe.csv"),
    student_code_file=os.path.join(PROJECT_ROOT, "data", "student_code2.py"),
    course_pdf_file=os.path.join(PROJECT_ROOT, "data", "course-context.pdf"),
    assignment_pdf_file=os.path.join(PROJECT_ROOT, "data", "a2-rest.pdf"),
    output_dir="research-artifacts/injected_cwes"
)
