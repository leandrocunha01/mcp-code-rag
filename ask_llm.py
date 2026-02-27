import psycopg2
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres.your-tenant-id",
    "password": "e2ae3572543ef1d80b281135f496cf1a",
    "host": "127.0.0.1",
    "port": "6543" 
}

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_context(query_text, limit=3):
    query_vector = embedding_model.encode(query_text).tolist()
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content, metadata 
            FROM framework_docs 
            ORDER BY embedding <=> %s::vector 
            LIMIT %s;
        """, (query_vector, limit))
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def ask_framework(question):
    relevant_chunks = retrieve_context(question, limit=4)
    if not relevant_chunks: return "Nenhum contexto encontrado."

    context_text = ""
    for idx, (content, metadata) in enumerate(relevant_chunks):
        file_path = metadata.get('file_path', 'Desconhecido')
        context_text += f"--- {file_path} ---\n{content}\n\n"

    system_prompt = f"""Você é um engenheiro especialista no framework PHP.
Use EXCLUSIVAMENTE os trechos abaixo para responder.
CONTEXTO:
{context_text}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(ask_framework("Como criar uma rota GET?"))
