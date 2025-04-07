import os
import json
from pathlib import Path
from crewai import Crew
from cwe_agent.ranker.cwe_ranker_agent import ranker, get_ranking_task, compute_weighted_score
from cwe_agent.helpers.io_utils import extract_text_from_pdf, load_student_code

def run_ranker_for_student(project_root: str, scored_dir: str, student_id: str, course_name: str, course_context: str, assignment_context: str):
    input_dir = Path(project_root) / scored_dir / student_id
    output_path = input_dir / "final_ranked_cwe.json"

    summaries = []
    for score_file in input_dir.glob("*_score.json"):
        with open(score_file, "r") as f:
            data = json.load(f)
            data["weighted_score"] = compute_weighted_score(data)
            summaries.append(data)

    # Sort summaries by descending weighted score before passing to LLM
    summaries.sort(key=lambda x: x["weighted_score"], reverse=True)

    task = get_ranking_task(evaluation_summaries=summaries, course_name=course_name, course_context=course_context, assignment_context=assignment_context)
    crew = Crew(agents=[ranker], tasks=[task], verbose=False)
    result = crew.kickoff()

    with open(output_path, "w") as f:
        json.dump(result.pydantic.model_dump(), f, indent=2)

    print(f"Ranking complete for {student_id} → {output_path.name}")

if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).parent.parent
    student_id = "student_code2"
    scored_dir = "research-artifacts/scored_cwes"
    course_name = "CMSC 426: Software as a Service"
    course_pdf = os.path.join(PROJECT_ROOT, "data/course-context.pdf")
    assignment_pdf = os.path.join(PROJECT_ROOT, "data/a2-rest.pdf")

    course_context = extract_text_from_pdf(course_pdf)
    assignment_context = extract_text_from_pdf(assignment_pdf)

    run_ranker_for_student(
        project_root=PROJECT_ROOT,
        scored_dir=scored_dir,
        student_id=student_id,
        course_name=course_name,
        course_context=course_context,
        assignment_context=assignment_context
    )