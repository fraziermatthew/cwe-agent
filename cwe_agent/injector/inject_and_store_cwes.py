import os
import json
import csv
from pathlib import Path
from crewai import Crew
from cwe_agent.injector.cwe_injector_agent import (
    injector,
    get_injection_task,
    infer_language_from_extension,
)
from cwe_agent.helpers.io_utils import extract_text_from_pdf, load_student_code


def parse_cwe_top25(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [
            {
                "cwe_id": row["CWE-ID"],
                "cwe_title": row["Name"],
                "cwe_description": row["Description"]
            }
            for row in reader
        ]

def inject_cwe_variants_for_student(
    project_root,
    cwe_csv_file,
    student_code_file,
    course_pdf_file,
    assignment_pdf_file,
    output_dir="research-artifacts/injected_cwes"
):

    # Load context
    course_text = extract_text_from_pdf(course_pdf_file)
    assignment_text = extract_text_from_pdf(assignment_pdf_file)
    student_code = load_student_code(student_code_file)
    language = infer_language_from_extension(student_code_file)

    # Load CWE list
    cwe_list = parse_cwe_top25(cwe_csv_file)

    # Output folder
    student_id = Path(student_code_file).stem
    student_output_dir = Path(project_root) / output_dir / student_id
    student_output_dir.mkdir(parents=True, exist_ok=True)

    for cwe in cwe_list:
        print(f"[Injecting] {cwe['cwe_id']} - {cwe['cwe_title']}")
        task = get_injection_task(student_code, course_text, assignment_text, cwe, language)
        crew = Crew(agents=[injector], tasks=[task], verbose=False)
        try:
            crew_output = crew.kickoff()

            # Uncomment optionally save raw version for traceability
            # raw_out_path = student_output_dir / f"{cwe['cwe_id']}_raw.txt"
            # with open(raw_out_path, "w", encoding="utf-8") as raw_f:
            #     raw_f.write(crew_output.raw)

            output_payload = {
                "cwe_id": cwe["cwe_id"],
                "cwe_title": cwe["cwe_title"],
                "cwe_description": cwe["cwe_description"],
                "language": language,
                "student_file": os.path.basename(student_code_file),
                "course_excerpt": course_text[:400],
                "assignment_excerpt": assignment_text[:400],
                "output": crew_output.pydantic.model_dump(),  # clean structured data
            }

            out_path = student_output_dir / f"CWE-{cwe['cwe_id']}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output_payload, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[ERROR] CWE {cwe['cwe_id']} failed to process: {e}")

    print(f"\n✅ Finished injecting all CWEs for: {student_code_file}")
    print(f"🗂 Stored in: {student_output_dir}")
