from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embeddings(content, bot_name):
    sentences = content.split('. ')                  # Splitting content into sentences
    sentences = [sentence.strip() for sentence in sentences if sentence]  # Remove empty sentences
    embeddings = model.encode(sentences)    #Encodes them into vector embeddings

    dim = embeddings.shape[1]                # get dim of embeddings
    print(f"Dim of embeddings: {dim}")
    index = faiss.IndexFlatL2(dim)           #Builds a FAISS index (for similarity search)
    index.add(np.array(embeddings))

    vector_path = f'instance/{bot_name}_index.faiss'       #Saves index to a file named {bot_name}_index.faiss
    faiss.write_index(index, vector_path)

    return vector_path