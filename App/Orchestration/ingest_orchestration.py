def ingest(path):

    text=parse_document(path)

    chunks=chunk(text)

    for i,c in enumerate(chunks):

        store_chunk(c,i)