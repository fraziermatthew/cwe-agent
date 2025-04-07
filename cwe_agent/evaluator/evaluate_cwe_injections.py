import os
import json
from pathlib import Path
from crewai import Crew
from cwe_agent.evaluator.cwe_evaluator_agent import evaluator, get_evaluation_task
from cwe_agent.helpers.io_utils import extract_text_from_pdf, load_student_code
from cwe_agent.helpers.diff import compute_diff_score


def evaluate_cwe_injections(
    project_root,
    injected_dir="research-artifacts/injected_cwes",
    output_dir="research-artifacts/scored_cwes",
    course_pdf="data/course-context.pdf",
    assignment_pdf="data/a2-rest.pdf",
    student_code_dir="data"
):
    # Extract shared context
    course_text = extract_text_from_pdf(os.path.join(project_root, course_pdf))
    assignment_text = extract_text_from_pdf(os.path.join(project_root, assignment_pdf))

    injected_student_path = Path(project_root) / injected_dir
    if not injected_student_path.exists():
        print(f"[ERROR] Injected folder not found: {injected_student_path}")
        return

    if not injected_student_path.is_dir():
        print(f"[SKIP] Not a directory: {injected_student_path}")
        return

    student_id = injected_student_path.name
    output_root = Path(project_root) / output_dir / student_id
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Evaluating folder: {injected_student_path}")
    for cwe_file in injected_student_path.glob("*.json"):
        try:
            print(f"  → Scoring file: {cwe_file.name}")
            with open(cwe_file, "r") as f:
                injected_data = json.load(f)

            original_code_path = os.path.join(
                project_root, student_code_dir, injected_data["student_file"]
            )
            original_code = load_student_code(original_code_path)
            injected_code = injected_data["output"]["modified_code"]

            # Compute similarity
            diff_score = compute_diff_score(original_code, injected_code)

            # Generate evaluation task
            task = get_evaluation_task(
                original_code=original_code,
                injected_code=injected_code,
                cwe_info={
                    "cwe_id": injected_data["cwe_id"],
                    "cwe_title": injected_data["cwe_title"],
                    "cwe_description": injected_data["cwe_description"]
                },
                course_context=course_text,
                assignment_context=assignment_text,
                diff_score=diff_score,
                language_name=injected_data.get("language", "plaintext")
            )
            crew = Crew(agents=[evaluator], tasks=[task], verbose=False)
            crew_output = crew.kickoff()

            result = crew_output.pydantic.dict()
            out_path = output_root / f"{injected_data['cwe_id']}_score.json"
            with open(out_path, "w") as score_file:
                json.dump(result, score_file, indent=2)

            print(f"Scored CWE {injected_data['cwe_id']} for {student_id}")

        except Exception as e:
            print(f"[ERROR] Failed to score {cwe_file.name}: {e}")
