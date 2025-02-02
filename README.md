# Demo - Analizando vulnerabilidades web usando LLMs

## Objetivo 
Demostrar cómo los modelos de lenguaje a gran escala (LLMs) pueden acelerar la detección y el análisis de vulnerabilidades web, integrando en un entorno de prueba un servidor intencionalmente vulnerable, una base de datos de registros y un servicio de LLM. Se busca evidenciar cómo la capacidad de procesamiento de lenguaje natural permite correlacionar datos, identificar patrones sospechosos y ofrecer sugerencias de mitigación o investigación en tiempo real, optimizando así la respuesta y la toma de decisiones en ciberseguridad.

![Demo LLMs](./imgs/llms.gif)


## Instalar el ambiente
### Requerimientos
- Instalar Docker
- Instalar docker compose
- Instalar Git CLI

### Instalación
Clonar el project `demo_llm`
```
```

- Ir al folder `demo_llm` para construir las imágenes y levantar los servicios
```bash
cd demo_llm
docker compose build
docker compose up -d
```

- Verifica que los contenedores estén arriba:
```bash
docker compose ps
```

- Instalar el modelo de ollama
```bash
docker exec -it ollama_llm ollama pull llama3
```

- Comprueba que `oLlama` corre en el puerto `11434`:
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [
    { "role": "user", "content": "Hola, oLlama. ¿Cómo estás?" }
  ]
}'
```
Deberías recibir una respuesta en texto proveniente del LLM dividido en chunks.


- Prueba de la Base de Datos. Conéctate al contenedor de PostgreSQL:
```bash
docker exec -it postgres_db psql -U user -d logsdb
```

- Muestra las tablas:
```bash
\dt
```
Debería existir la tabla `nginx_logs`.

- Sal de psql con:
```bash
\q
```

- Prueba del Servicio Nginx y Inserción de Logs. Realiza llamadas de prueba al servicio Nginx en http://localhost:8080, incluyendo un id malicioso (SQLi):
```
curl "http://localhost:8080/"
curl "http://localhost:8080/?id=1"
curl "http://localhost:8080/?id=' OR 1=1 --"
curl "http://localhost:8080/?id=1' UNION SELECT null, null, null --"
curl "http://localhost:8080/?id='; --"
curl "http://localhost:8080/?id=1' AND 'a'='a --"
```

- Verifica los logs en la base de datos. Vuelve a psql:
```bash
docker exec -it postgres_db psql -U user -d logsdb
```

- Corre la consulta:
```bash
SELECT * FROM nginx_logs;
```

- Sal con `\q`.

Si todo funciona correctamente, significa que Nginx está registrando los accesos y el script `log_to_db.py` está insertando esos accesos en la tabla `nginx_logs`.

### Análisis de logs usando LLMs
Prueba el Programa en Python `collect_logs.py` para hacer el análisis de los logs.

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=user
export DB_PASSWORD=pass
export DB_NAME=logsdb
export OLLAMA_URL=http://localhost:11434
```

- Instala las librerias requeridas de python en un environment
```bash
python3 -m venv env
source env/bin/activate
pip3 install psycopg2 requests
```

- Ejecuta el script:
```bash
cd python-client
./collect_logs.py
```

Verás en consola los últimos 5 logs. Luego te pedirá una pregunta.

El script enviará los logs y tu pregunta al LLM a través de la API de oLlama. Deberías recibir alguna respuesta basada en el modelo que tengas cargado.

Podrías preguntar:
```
Existe algún tipo de ataque en los logs? Y cuales son las recomendaciones para investigar y mitigar?
```

## Detener el ambiente
Para detener el ambiente, ejecutar el siguiente comando:
```bash
docker compose down
```