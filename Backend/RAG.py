from sentence_transformers import SentenceTransformer
import numpy as np  
import faiss

model = SentenceTransformer('all-MiniLM-L6-v2')

def chunker(text, chunk_size=100):

    """Splits text into chunks of specified size"""

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

def create_embeddings(chunks):

    embeddings = model.encode(chunks)
    return np.array(embeddings)

def build_faiss_index(embeddings):

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def retrieve_relevant_chunks(query, index, chunks, top_k=1):

    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    relevant_chunks = [chunks[i] for i in indices[0]]
    return relevant_chunks