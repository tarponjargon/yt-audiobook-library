#!/bin/bash

# Wait for postgres to be ready
echo "Waiting for postgres to be ready..."
until PGPASSWORD=${POSTGRES_PASSWORD} psql -h postgres -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing backup"

# Run the backup
PGPASSWORD=${POSTGRES_PASSWORD} pg_dump -h postgres -U ${POSTGRES_USER} ${POSTGRES_DB} > /init_data/ytbooks_dump.sql

echo "Initialization dump updated: /init_data/ytbooks_dump.sql"
