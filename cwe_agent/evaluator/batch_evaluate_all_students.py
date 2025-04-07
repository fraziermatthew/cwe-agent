import os
from pathlib import Path
from cwe_agent.evaluator.evaluate_cwe_injections import evaluate_cwe_injections

def batch_evaluate_all_students():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    injected_root = Path(project_root) / "research-artifacts/injected_cwes"

    if not injected_root.exists():
        print(f"[ERROR] Injected CWE folder not found: {injected_root}")
        return

    for student_folder in injected_root.iterdir():
        if not student_folder.is_dir():
            continue

        print(f"\nEvaluating student: {student_folder.name}")
        evaluate_cwe_injections(
            project_root=project_root,
            injected_dir=f"research-artifacts/injected_cwes/{student_folder.name}",
            output_dir="research-artifacts/scored_cwes",
            course_pdf="data/course-context.pdf",
            assignment_pdf="data/a2-rest.pdf",
            student_code_dir="data"
        )

if __name__ == "__main__":
    batch_evaluate_all_students()
