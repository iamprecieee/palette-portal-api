#!/bin/bash

echo "Make migrations"
python manage.py makemigrations

echo "Apply new migrations"
python manage.py migrate

echo "Generate SSL certificate"
python ssl_cert_generator.py

echo "Generate drf_spectacular schema"
python manage.py spectacular --api-version "1.0.0" --file schema.yml --validate

exec "$@"