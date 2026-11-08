from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings


splitter = RecursiveCharacterTextSplitter(

    chunk_size=settings.CHUNK_SIZE,

    chunk_overlap=settings.CHUNK_OVERLAP,
)


def chunk_text(text):

    return splitter.split_text(text)