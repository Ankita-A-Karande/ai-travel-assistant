# services/file_loader.py

from docx import Document
import PyPDF2

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")

def read_file_content(file):
    """
    Read uploaded file and return text content.
    Supports txt, docx, pdf.
    """
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        return ""

    if file.filename.lower().endswith(".txt"):
        return file.file.read().decode("utf-8")

    elif file.filename.lower().endswith(".docx"):
        doc = Document(file.file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file.filename.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    return ""