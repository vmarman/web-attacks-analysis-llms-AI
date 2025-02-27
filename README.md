## Demo - Analyzing Web Vulnerabilities Using LLMs and AI

Demonstrate how large language models (LLMs) can accelerate web vulnerability detection and analysis with the help of Artificial Intelligence, integrating an intentionally vulnerable server, a log database, and an LLM service into a test environment. The goal is to showcase how natural language processing capabilities enable data correlation, identification of suspicious patterns, and real-time mitigation or investigation suggestions, thereby optimizing response and decision-making in cybersecurity.

### Installation  
Clone the project `web-attacks-analysis-llms-AI
`  
```
```

- Go to the `web-attacks-analysis-llms-AI
` folder to build the images and start the services  
```bash
cd web-attacks-analysis-llms-AI

docker compose build
docker compose up -d
```

- Verify that the containers are up:  
```bash
docker compose ps
```

- Install the Ollama model  
```bash
docker exec -it ollama_llm ollama pull llama3
```

- Check that `oLlama` is running on port `11434`:  
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [
    { "role": "user", "content": "Hello, oLlama. How are you?" }
  ]
}'
```
You should receive a text response from the LLM in chunks.

### Database Test  
- Connect to the PostgreSQL container:  
```bash
docker exec -it postgres_db psql -U user -d logsdb
```

- Show the tables:  
```bash
\dt
```
The table `nginx_logs` should exist.

- Exit psql with:  
```bash
\q
```

### Nginx Service and Log Insertion Test  
Make test requests to the Nginx service at http://localhost:8080, including a malicious ID (SQLi):  
```
curl "http://localhost:8080/"
curl "http://localhost:8080/?id=1"
curl "http://localhost:8080/?id=' OR 1=1 --"
curl "http://localhost:8080/?id=1' UNION SELECT null, null, null --"
curl "http://localhost:8080/?id='; --"
curl "http://localhost:8080/?id=1' AND 'a'='a --"
```

- Check the logs in the database. Return to psql:  
```bash
docker exec -it postgres_db psql -U user -d logsdb
```

- Run the query:  
```bash
SELECT * FROM nginx_logs;
```

- Exit with `\q`.

If everything works correctly, it means that Nginx is logging access, and the `log_to_db.py` script is inserting those logs into the `nginx_logs` table.

### Log Analysis Using LLMs  
Test the Python program `collect_logs.py` to analyze the logs.  

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=user
export DB_PASSWORD=pass
export DB_NAME=logsdb
export OLLAMA_URL=http://localhost:11434
```

- Install the required Python libraries in a virtual environment  
```bash
python3 -m venv env
source env/bin/activate
pip3 install psycopg2 requests
```

- Run the script:  
```bash
cd python-client
./collect_logs.py
```

You will see the last five logs in the console. Then, it will ask you a question.  

The script will send the logs and your question to the LLM through the oLlama API. You should receive a response based on the loaded model.  

You could ask:  
```
Are there any attacks in the logs? What are the recommendations for investigation and mitigation?
```

## Stop the Environment  
To stop the environment, run the following command:  
```bash
docker compose down
```

