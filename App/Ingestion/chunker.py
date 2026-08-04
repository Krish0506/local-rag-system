from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)


def chunk_text(text: str) -> list[str]:
    """
    Split a large document into smaller overlapping chunks.
    """
    return splitter.split_text(text)