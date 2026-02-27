import psycopg2
import json
from sentence_transformers import SentenceTransformer

print("Carregando modelo na memória...")
model = SentenceTransformer('all-MiniLM-L6-v2')

DB_CONFIG = {
    "dbname": "sua_base",
    "user": "seu_usuario",
    "password": "sua_senha",
    "host": "localhost",
    "port": "5432"
}

documents = [
    {
        "content": "public static function get(string $uri, callable $action) { self::$routes['GET'][$uri] = $action; }",
        "metadata": {"file": "Router.php", "type": "method"}
    },
    {
        "content": "Route::get('/api/users', [UserController::class, 'index']);",
        "metadata": {"file": "routes.php", "type": "implementation"}
    }
]

def setup_database(cursor):
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS framework_docs (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            metadata JSONB,
            embedding vector(384)
        );
    """)

def ingest_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        setup_database(cursor)
        conn.commit()

        print("Gerando tensores e inserindo no banco...")
        for doc in documents:
            content = doc["content"]
            metadata = doc["metadata"]
            embedding = model.encode(content).tolist()
            
            cursor.execute("""
                INSERT INTO framework_docs (content, metadata, embedding)
                VALUES (%s, %s, %s::vector)
            """, (content, json.dumps(metadata), embedding))
            
        conn.commit()
        print(f"{len(documents)} chunks vetorizados e salvos com sucesso.")

    except Exception as e:
        print(f"Erro: {e}")
        if conn: conn.rollback()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    ingest_data()
