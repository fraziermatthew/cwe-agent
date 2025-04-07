import os
import json
from pydantic import BaseModel
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

# === Set up LLM ===
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY"),
)

class RankedCWEs(BaseModel):
    ranked_cwes: list[str]
    top_choice: str
    rationale: str

ranker = Agent(
    role="CWE Ranking Agent",
    goal="Identify the most educational CWE for a student submission",
    backstory=(
        "You are an expert in secure coding education. Given a set of CWE injections and their evaluation scores, "
        "your task is to rank them based on their total educational value. You prioritize CWE relevance, "
        "pedagogical value, appropriateness to the course level, and naturalness of code integration. "
        "In cases of ties, consider qualitative factors like learning impact and realism."
        "Your response must be in JSON format:\n"
        "{\n"
        "  \"ranked_cwes\": \"[\"CWE-20\", \"CWE-22\", \"CWE-94\", ...]\",\n"
        "  \"top_choice\": \"CWE-20\",\n"
        "  \"rationale\": \"Explain why this CWE is the best educational fit.\"\n"
        "}"
    ),
    allow_delegation=False,
    # verbose=True,
    llm=llm,
)

# def get_ranking_task(evaluation_summaries: list[dict], course_name: str) -> Task:
#     prompt = f"""
# You are ranking CWE injection variants for a student in the course: "{course_name}".

# You are given the following CWE evaluations:

# {json.dumps(evaluation_summaries, indent=2)}

# Rank these CWE injections in order of most to least educational for the student.

# Guidelines:
# - Prioritize high relevance and pedagogical value.
# - Use naturalness and appropriateness to break ties.
# - If two are very close in score, prefer the CWE that best aligns with real-world scenarios or that teaches a key secure coding principle.
# - Pick a single CWE as the best learning opportunity.

# Return your response in this exact JSON format:
# {{
#   "ranked_cwes": ["CWE-20", "CWE-22", "CWE-94", ...],
#   "top_choice": "CWE-20",
#   "rationale": "Explain why this CWE is the best educational fit."
# }}
#     """

#     return Task(
#         description=prompt,
#         agent=ranker,
#         expected_output="JSON object with ranking and rationale",
#         output_pydantic=RankedCWEs
#     )
    
def get_ranking_task(evaluation_summaries: list[dict], course_name: str, course_context: str, assignment_context: str) -> Task:
    prompt = f"""
You are ranking CWE injection variants for a student in the course: "{course_name}".

Course Context:
{course_context}

Assignment Context:
{assignment_context}

You are given the following CWE evaluations:
{json.dumps(evaluation_summaries, indent=2)}

Rank these CWE injections in order of most to least educational for the student.

Guidelines:
- Prioritize high relevance and pedagogical value.
- Use naturalness and appropriateness to break ties.
- Consider how well each CWE fits the actual course content and assignment.
- Pick a single CWE as the best learning opportunity.

Return your response in this exact JSON format:
{{
  "ranked_cwes": ["CWE-20", "CWE-22", "CWE-94", ...],
  "top_choice": "CWE-20",
  "rationale": "Explain why this CWE is the best educational fit."
}}
"""
    return Task(
        description=prompt,
        agent=ranker,
        expected_output="JSON object with ranking and rationale",
        output_pydantic=RankedCWEs
    )

def compute_weighted_score(entry: dict) -> float:
    return (
        entry["relevance"] * 3 +
        entry["pedagogical_value"] * 3 +
        entry["appropriateness"] * 2 +
        entry["naturalness"] * 1
    )
    
