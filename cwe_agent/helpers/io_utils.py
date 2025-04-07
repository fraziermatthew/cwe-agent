from pathlib import Path
from PyPDF2 import PdfReader

def load_student_code(file_path: str) -> str:
    return Path(file_path).read_text()

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(
        [page.extract_text() for page in reader.pages if page.extract_text()]
    )