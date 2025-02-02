FROM python:3.9-slim-bullseye AS builder
# Instalamos Nginx y dependencias
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
RUN pip install psycopg2-binary

# Creamos directorio para nuestra app
RUN mkdir -p /app
WORKDIR /app

# Copiamos el archivo de configuración de Nginx y el script de logs
COPY nginx.conf /etc/nginx/nginx.conf
COPY log_to_db.py /app/

# Exponemos el puerto 80
EXPOSE 80

# Copiamos un script de arranque para iniciar todo en paralelo (Nginx + script Python)
# Podríamos usar supervisord o un script shell simple
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]