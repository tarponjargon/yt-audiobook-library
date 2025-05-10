#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Check if the database is already populated
TABLES=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" -t | xargs)

if [ "$TABLES" -eq "0" ]; then
  echo "Initializing database with dump file..."
  # Use psql to import the dump file with error handling
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/ytbooks_dump.sql || {
    echo "Error importing database dump. Check the SQL file for syntax errors."
    exit 1
  }
  echo "Database initialization completed."
else
  echo "Database already contains tables. Skipping initialization."
fi
