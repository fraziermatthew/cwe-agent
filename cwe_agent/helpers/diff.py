from difflib import SequenceMatcher

def compute_diff_score(original: str, modified: str) -> float:
    return SequenceMatcher(None, original, modified).ratio() * 100
