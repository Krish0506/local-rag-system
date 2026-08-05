from pathlib import Path

from app.ingestion.loaders import (
    load_csv,
    load_docx,
    load_excel,
    load_pdf,
    load_txt,
)


def parse_document(path):

    suffix = Path(path).suffix.lower()

    if suffix == ".pdf":
        return load_pdf(path)

    elif suffix == ".docx":
        return load_docx(path)

    elif suffix == ".txt":
        return load_txt(path)

    elif suffix == ".csv":
        return load_csv(path)

    elif suffix in [".xls", ".xlsx"]:
        return load_excel(path)

    else:
        raise ValueError(f"Unsupported file type: {suffix}")