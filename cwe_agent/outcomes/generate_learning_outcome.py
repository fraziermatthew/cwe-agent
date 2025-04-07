import json
import os
from pathlib import Path
from crewai import Crew
from cwe_agent.outcomes.learning_outcome_agent import generator, get_learning_outcome_task
from cwe_agent.helpers.io_utils import load_student_code, extract_text_from_pdf

def run_learning_outcome_pipeline(project_root: str, student_id: str):
    scored_dir = Path(project_root) / "research-artifacts/scored_cwes" / student_id
    injected_dir = Path(project_root) / "research-artifacts/injected_cwes" / student_id
    student_code_dir = Path(project_root) / "data"
    outcome_path = scored_dir / "learning_outcome.json"

    # Load final ranked CWE
    ranked_path = scored_dir / "final_ranked_cwe.json"
    if not ranked_path.exists():
        raise FileNotFoundError(f"Missing final_ranked_cwe.json for {student_id}")

    with open(ranked_path, "r") as f:
        ranked_data = json.load(f)

    top_cwe_id = ranked_data["top_choice"]
    rationale = ranked_data["rationale"]

    # Find the CWE file that matches
    cwe_file = injected_dir / f"{top_cwe_id}.json"
    if not cwe_file.exists():
        raise FileNotFoundError(f"Missing injected CWE file: {cwe_file}")

    with open(cwe_file, "r") as f:
        cwe_data = json.load(f)

    original_code_path = student_code_dir / cwe_data["student_file"]
    original_code = load_student_code(original_code_path)
    injected_code = cwe_data["output"]["modified_code"]

    # Context
    course_context = extract_text_from_pdf(os.path.join(project_root, "data/course-context.pdf"))
    assignment_context = extract_text_from_pdf(os.path.join(project_root, "data/a2-rest.pdf"))

    task = get_learning_outcome_task(
        original_code=original_code,
        injected_code=injected_code,
        cwe_id=cwe_data["cwe_id"],
        cwe_title=cwe_data["cwe_title"],
        rationale=rationale,
        course_context=course_context,
        assignment_context=assignment_context
    )

    crew = Crew(agents=[generator], tasks=[task], verbose=False)
    result = crew.kickoff()

    with open(outcome_path, "w") as f:
        json.dump(result.pydantic.model_dump(), f, indent=2)

    print(f"🎓 Learning outcome generated for {student_id} → {outcome_path.name}")

if __name__ == "__main__":
    student_id = "student_code2"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_learning_outcome_pipeline(project_root, student_id)
