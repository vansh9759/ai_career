import os
import re

def extract_text_from_filepath(file_path):
    """
    Extracts text from PDF, DOCX, or TXT files using multiple fallback mechanisms.
    """
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        # 1. Try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except Exception:
            pass

        # 2. Try PyPDF2 / pypdf fallback if empty
        if not text.strip():
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            text += t + "\n"
            except Exception:
                pass

        # 3. Try pypdf fallback if empty
        if not text.strip():
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
            except Exception:
                pass

        # 4. Regex binary stream fallback if PDF parsers missing/failed
        if not text.strip():
            try:
                with open(file_path, "rb") as f:
                    content = f.read().decode("latin-1", errors="ignore")
                    # Extract printable text sequences inside PDF objects
                    matches = re.findall(r'\(([^()]{3,})\)\s*Tj', content)
                    if matches:
                        text = " ".join(matches)
                    else:
                        # Fallback printable ASCII strings
                        printable = re.findall(r'[a-zA-Z0-9\s.,;:\-@#%&*()+=\[\]/]{4,}', content)
                        text = " ".join(printable)
            except Exception:
                pass

    elif ext == ".docx":
        try:
            from docx import Document
            doc = Document(file_path)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception:
            pass

    elif ext in [".txt", ".md"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            pass

    return text.strip()