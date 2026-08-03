from pathlib import Path

from .loaders import *

def parse_document(path):

    suffix=Path(path).suffix.lower()

    if suffix==".pdf":

        return load_pdf(path)

    elif suffix==".docx":

        return load_docx(path)

    elif suffix==".csv":

        return load_csv(path)

    elif suffix==".xlsx":

        return load_excel(path)

    elif suffix==".txt":

        return load_txt(path)

    else:

        raise Exception("Unsupported file")