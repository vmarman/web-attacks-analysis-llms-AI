import os
import time
import psycopg2
import subprocess

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', 'user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'pass')
DB_NAME = os.environ.get('DB_NAME', 'logsdb')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Creamos la tabla logs si no existe
def create_logs_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nginx_logs (
            id SERIAL PRIMARY KEY,
            log_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_log_line(line):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO nginx_logs (log_text) VALUES (%s)", (line,))
    conn.commit()
    cur.close()
    conn.close()

def main():
    # Asegurarnos de que la tabla exista
    create_logs_table()

    print("Iniciando monitoreo de /var/log/nginx/access.log...")
    # tail -F sigue el archivo aunque se rote
    process = subprocess.Popen(["tail", "-F", "/var/log/nginx/access.log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        line = process.stdout.readline()
        if line:
            # Cada línea del log la insertamos en la base
            insert_log_line(line.strip())
        time.sleep(0.1)

if __name__ == "__main__":
    main()