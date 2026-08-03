from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter=RecursiveCharacterTextSplitter(

chunk_size=1000,

chunk_overlap=200

)

def chunk(text):

    return splitter.split_text(text)