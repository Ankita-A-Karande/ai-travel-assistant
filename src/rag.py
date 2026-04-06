# services/rag.py

from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Initialize embedding model once
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def create_vector_store(text):
    """
    Chunk text and create FAISS vector index.
    """
    splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_text(text)

    embeddings = embedding_model.encode(chunks)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return index, chunks

def retrieve_chunks(query, index, chunks, k=3):
    """
    Retrieve top-k most relevant chunks for a query.
    """
    query_emb = embedding_model.encode([query])
    D, I = index.search(np.array(query_emb), k)
    retrieved = []
    seen = set()
    for i in I[0]:
        chunk = chunks[i].strip()
        if chunk not in seen:
            retrieved.append(chunk)
            seen.add(chunk)
    return retrieved
    #return [chunks[i] for i in I[0]]