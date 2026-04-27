import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

df = pd.read_csv(r"C:\Users\Prajjwal\OneDrive\Desktop\Projects\GenAi\ResumeAnalyzer\data\final_interview_questions.csv")

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="interview_questions"
)

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = df["question"].tolist()
categories = df["category"].tolist()

batch_size = 5000

for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i+batch_size]
    batch_categories = categories[i:i+batch_size]

    batch_embeddings = model.encode(batch_docs).tolist()
    batch_ids = [f"q_{j}" for j in range(i, i + len(batch_docs))]

    collection.add(
        ids=batch_ids,
        documents=batch_docs,
        embeddings=batch_embeddings,
        metadatas=[
            {"category": cat} for cat in batch_categories
        ]
    )

    print(f"Inserted batch {i} to {i + len(batch_docs)}")

print("All data inserted successfully!")