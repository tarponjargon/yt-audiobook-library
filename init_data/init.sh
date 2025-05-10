#!/bin/bash
set -e

# Wait for PostgreSQL to be ready - don't use localhost
until pg_isready -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Check if the database is already populated
echo "Checking if database is already populated..."
TABLES=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" -t | xargs)
echo "Found $TABLES tables in database"

if [ "$TABLES" -eq "0" ] || [ -z "$TABLES" ]; then
  echo "Initializing database with dump file..."
  # Use psql to import the dump file with error handling
  echo "Starting database import..."
  cat /docker-entrypoint-initdb.d/ytbooks_dump.sql | psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" || {
    echo "Error importing database dump. Check the SQL file for syntax errors."
    exit 1
  }
  echo "Import command completed"
  echo "Database initialization completed."
else
  echo "Database already contains tables. Skipping initialization."
fi
