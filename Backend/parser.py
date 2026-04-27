import pdfplumber
import docx

# Extract text from PDF
def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Extract text from DOCX
def extract_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Extract text from TXT
def extract_txt(file):
    return file.read().decode("utf-8")

# Main handler
def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_docx(file)
    elif file.name.endswith(".txt"):
        return extract_txt(file)
    else:
        return "Unsupported file format"