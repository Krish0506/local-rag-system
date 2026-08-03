from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

def load_txt(path):

    with open(path,encoding="utf8") as f:

        return f.read()

def load_excel(path):

    df=pd.read_excel(path)

    return df.to_string()

def load_csv(path):

    df=pd.read_csv(path)

    return df.to_string()

def load_docx(path):

    doc=Document(path)

    return "\n".join(
        p.text
        for p in doc.paragraphs
    )

def load_pdf(path):

    reader=PdfReader(path)

    text=""

    for page in reader.pages:

        text+=page.extract_text()

    return text