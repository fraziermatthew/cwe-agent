import os
import time
from pathlib import Path
from cwe_agent.injector.inject_and_store_cwes import inject_cwe_variants_for_student
from cwe_agent.evaluator.evaluate_cwe_injections import evaluate_cwe_injections
from cwe_agent.ranker.rank_cwe_evaluations import run_ranker_for_student
from cwe_agent.outcomes.generate_learning_outcome import run_learning_outcome_pipeline
from cwe_agent.helpers.io_utils import extract_text_from_pdf



def run_pipeline(project_root: str, student_id: str):
    print("\n=== Running full CWE educational pipeline ===")
    start_time = time.time()

    # === 1. Inject Top 25 CWEs into code ===
    print("\n[1/4] Injecting CWE vulnerabilities...")
    inject_cwe_variants_for_student(
        project_root=project_root,
        cwe_csv_file=os.path.join(project_root, "data", "cwe.csv"),
        student_code_file=os.path.join(project_root, "data", "student_code2.py"),
        course_pdf_file=os.path.join(project_root, "data", "course-context.pdf"),
        assignment_pdf_file=os.path.join(project_root, "data", "a2-rest.pdf"),
        output_dir="research-artifacts/injected_cwes"
    )

    # === 2. Evaluate CWE injection quality ===
    print("\n[2/4] Evaluating CWE injection quality...")
    evaluate_cwe_injections(
        project_root=project_root,
        injected_dir= f"research-artifacts/injected_cwes/{student_id}",
        output_dir= "research-artifacts/scored_cwes",
        course_pdf= "data/course-context.pdf",
        assignment_pdf= "data/a2-rest.pdf",
        student_code_dir= "data"
    )

    # === 3. Rank the most educational CWE ===
    print("\n[3/4] Ranking CWE effectiveness...")
    course_context = extract_text_from_pdf(os.path.join(project_root, "data/course-context.pdf"))
    assignment_context = extract_text_from_pdf(os.path.join(project_root, "data/a2-rest.pdf"))

    run_ranker_for_student(
        project_root=project_root,
        scored_dir=os.path.join(project_root, "research-artifacts/scored_cwes"),
        student_id=student_id,
        course_name="CMSC 426: Software as a Service",
        course_context=course_context,
        assignment_context=assignment_context
    )

    # === 4. Generate the learning outcome ===
    print("\n[4/4] Generating student learning outcome...")
    run_learning_outcome_pipeline(
        project_root=project_root,
        student_id=student_id
    )

    total_time = time.time() - start_time
    print(f"\nAll agents complete. Educational output ready! Total time: {total_time:.2f} seconds.")


if __name__ == "__main__":
    student_id = "student_code2"  # update as needed
    project_root = Path(__file__).parent
    print('project_root:', project_root)
    run_pipeline(project_root, student_id)
