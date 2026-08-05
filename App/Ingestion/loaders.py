from pathlib import Path

import pandas as pd
from PyPDF2 import PdfReader
from docx import Document


def load_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    return text


def load_docx(path):

    document = Document(path)

    return "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )


def load_txt(path):

    return Path(path).read_text(
        encoding="utf-8",
        errors="ignore"
    )


def load_csv(path):

    dataframe = pd.read_csv(path)

    return dataframe.to_string(index=False)


def load_excel(path):

    dataframe = pd.read_excel(path)

    return dataframe.to_string(index=False)