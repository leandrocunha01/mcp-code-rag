import argparse
import psycopg2
import psycopg2.extras
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 1. Configurações de Ambiente
FRAMEWORK_DIR = "/home/leandro/Development/Eloco-Api" 
DEFAULT_MODEL = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 1500 
BATCH_SIZE = 64 

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres.your-tenant-id",
    "password": "e2ae3572543ef1d80b281135f496cf1a",
    "host": "127.0.0.1",
    "port": "6543" 
}

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

def chunk_text(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def process_and_insert_batch(cursor, model, contents, metadata_list):
    """
    Executa a inferência neural paralela e o envio do lote via TCP/IP.
    Não realiza o commit aqui, apenas a execução no buffer do Postgres.
    """
    if not contents:
        return
        
    embeddings = model.encode(contents).tolist()
    
    records = [
        (content, json.dumps(meta), emb) 
        for content, meta, emb in zip(contents, metadata_list, embeddings)
    ]
    
    psycopg2.extras.execute_values(
        cursor,
        "INSERT INTO framework_docs (content, metadata, embedding) VALUES %s",
        records,
        template="(%s, %s, %s::vector)"
    )

def ingest_directory(base_path: Path, model_name: str, file_pattern: str):
    print("Carregando pesos neurais (SentenceTransformer) na memória...")
    model = SentenceTransformer(model_name)
    
    php_files = list(base_path.rglob(file_pattern))
    
    if not php_files:
        print(f"Nenhum arquivo correspondente a '{file_pattern}' encontrado em {base_path}.")
        return

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()# 1. Configurações de Ambiente
        setup_database(cursor)
        conn.commit() # Efetiva a criação da tabela logo no início
        
        total_chunks_inserted = 0
        batch_contents = []
        batch_metadata = []

        print(f"Iniciando varredura e vetorização de {len(php_files)} arquivos...")

        for file_path in php_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception:
                # Ignora arquivos que o S.O. não conseguir ler (permissão, encoding quebrado)
                continue
                
            chunks = chunk_text(file_content, CHUNK_SIZE)
            
            for chunk_index, chunk_content in enumerate(chunks):
                clean_chunk = chunk_content.strip()
                if not clean_chunk: 
                    continue

                batch_contents.append(clean_chunk)
                batch_metadata.append({
                    "file_path": str(file_path.relative_to(base_path)),
                    "chunk_index": chunk_index
                })
                
                # Quando o lote atinge 64 elementos, disparamos o processamento
                if len(batch_contents) >= BATCH_SIZE:
                    try:
                        # 1. Tenta executar o lote e gravar no disco
                        process_and_insert_batch(cursor, model, batch_contents, batch_metadata)
                        conn.commit() 
                        total_chunks_inserted += len(batch_contents)
                        print(f"Progresso: {total_chunks_inserted} blocos consolidados no banco...")
                    except Exception as batch_error:
                        # 2. Em caso de falha (ex: caractere nulo não aceito pelo Postgres)
                        print(f"[!] Erro no lote. Ignorando {len(batch_contents)} chunks. Falha: {batch_error}")
                        # 3. Reverte o estado transacional do banco
                        conn.rollback()
                    finally:
                        # 4. Limpa a memória RAM independentemente de sucesso ou falha
                        batch_contents.clear()
                        batch_metadata.clear()
        
        # Processa o lote residual final (dados que não atingiram o tamanho exato do BATCH_SIZE)
        if batch_contents:
            try:
                process_and_insert_batch(cursor, model, batch_contents, batch_metadata)
                conn.commit()
                total_chunks_inserted += len(batch_contents)
            except Exception as e:
                print(f"[!] Erro no lote residual. Falha: {e}")
                conn.rollback()
                
        print(f"\nOperação concluída. Total de blocos vetorizados e salvos: {total_chunks_inserted}.")

    except Exception as fatal_error:
        print(f"Falha crítica na conexão ou no driver de I/O: {fatal_error}")
    finally:
        # Garante o fechamento seguro dos sockets TCP e liberação de recursos do S.O.
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingestão recursiva de arquivos PHP para vetorizar e armazenar no Postgres."
    )
    parser.add_argument(
        "--path", "-p",
        default=FRAMEWORK_DIR,
        help="Diretório base onde os arquivos serão procurados (ex: /home/user/projeto)."
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help="Nome do modelo SentenceTransformer a ser usado (linguagem)."
    )
    parser.add_argument(
        "--pattern", "-t",
        default="*.php",
        help="Padrão de arquivo usado pelo glob (ex: '*.php', '*.js')."
    )

    args = parser.parse_args()
    ingest_directory(Path(args.path), args.model, args.pattern)