import re


def clean_text(text):

    text = text.replace("\t", " ")

    text = text.replace("\r", " ")

    text = re.sub(r"\n+", "\n", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()