#!/usr/bin/env python3
import time
import psycopg2
import requests
import os
import json

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', 'user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'pass')
DB_NAME = os.environ.get('DB_NAME', 'logsdb')

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11411')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def fetch_logs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT log_text FROM nginx_logs ORDER BY created_at DESC LIMIT 5;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]

def ask_llm(prompt):
# curl http://localhost:11434/api/chat -d '{
#   "model": "llama3.2",
#   "messages": [
#     { "role": "user", "content": "why is the sky blue?" }
#   ]
# }'
    url = f"{OLLAMA_URL}/api/chat"
    data = {"model":"llama3",
            "messages":[
                {
                    "role": "user",
                    "content": prompt
                }]
                        }
    try:
        response = requests.post(url, json=data, stream=True)
        if response.status_code == 200:
            full_response = ""
            start_time = time.time()
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    chuckutf = chunk.decode('utf-8')
                    chunkjson = json.loads(chuckutf)
                    content = chunkjson['message']['content']
                    full_response += content

                    print(f"Progress: {round((time.time() - start_time), 2)}s", end='\r')
            return full_response
        else:
            return f"Error consultando LLM: {response.text}"
    except Exception as e:
        return f"Excepción consultando LLM: {e}"

def main():
    print("Recolectando los últimos 5 logs de Nginx:")
    logs = fetch_logs()
    for i, log_line in enumerate(logs, start=1):
        print(f"{i}. {log_line}")

    user_prompt = input("\nIngresa una pregunta para el LLM sobre estos logs:\n> ")
    prompt_text = f"Estos son los últimos 5 logs:\n\n{logs}\n\nPregunta del usuario: {user_prompt}"
    response = ask_llm(prompt_text)
    print("\nRespuesta del LLM:\n", response)

if __name__ == "__main__":
    main()