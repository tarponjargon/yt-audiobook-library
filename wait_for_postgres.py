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
    
    while True:
        try:
            conn = psycopg2.connect(
                host=postgres_host,
                port=postgres_port,
                dbname=postgres_db,
                user=postgres_user,
                password=postgres_password
            )
            conn.close()
            print("Connected to PostgreSQL!")
            break
        except OperationalError:
            print("PostgreSQL not ready yet, waiting...")
            time.sleep(2)

if __name__ == "__main__":
    wait_for_postgres()
