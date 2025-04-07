CWE_RANKER_USR_PROMPT = """You are given a list of evaluated CWE injections. Each has a total score and evaluator notes.

Rank them by educational impact.

CWE Evaluations:
{evaluated_cwe_list}"""