#!/bin/bash

# Iniciar Nginx en segundo plano
echo "Iniciando Nginx..."
service nginx start

# Iniciar el script de Python que lee logs e inserta en la BD
echo "Iniciando script log_to_db.py..."
python /app/log_to_db.py