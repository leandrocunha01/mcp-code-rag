import psycopg2
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer

mcp = FastMCP(name="PHP_Framework_RAG", port=8199, host="0.0.0.0")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres.your-tenant-id",
    "password": "e2ae3572543ef1d80b281135f496cf1a",
    "host": "127.0.0.1",
    "port": "6543" 
}

@mcp.tool()
def buscar_codigo_framework(query: str, limit: int = 3) -> str:
    """Busca trechos de código no framework PHP proprietário."""
    query_vector = embedding_model.encode(query).tolist()
    conn = None; cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content, metadata 
            FROM framework_docs 
            ORDER BY embedding <=> %s::vector 
            LIMIT %s;
        """, (query_vector, limit))
        
        results = cursor.fetchall()
        if not results: return "Sem contexto."

        context_output = "CONTEXTO:\n\n"
        for _, (content, metadata) in enumerate(results):
            context_output += f"--- Arquivo: {metadata.get('file_path')} ---\n{content}\n\n"
        return context_output
    except Exception as e:
        return str(e)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    mcp.run(transport="sse")
