import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH")

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="documents"
)