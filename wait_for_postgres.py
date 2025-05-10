import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres():
    postgres_host = os.getenv("DB_HOST", "postgres")
    postgres_port = os.getenv("DB_PORT", "5432")
    postgres_db = os.getenv("DB_NAME")
    postgres_user = os.getenv("DB_USER")
    postgres_password = os.getenv("DB_PASSWORD")
    
    max_retries = 30
    retry_count = 0
    
    print(f"Waiting for PostgreSQL at {postgres_host}:{postgres_port}...")
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=postgres_host,
                port=postgres_port,
                dbname=postgres_db,
                user=postgres_user,
                password=postgres_password
            )
            conn.close()
            print("Successfully connected to PostgreSQL!")
            return
        except OperationalError as e:
            retry_count += 1
            print(f"PostgreSQL not ready yet (attempt {retry_count}/{max_retries}): {str(e)}")
            time.sleep(2)
    
    print("Failed to connect to PostgreSQL after maximum retries")
    exit(1)

if __name__ == "__main__":
    wait_for_postgres()
