#!/bin/bash
set -e

# Print environment variables for debugging (without showing passwords)
echo "Environment variables:"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "PGHOST: $PGHOST"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready; do
  echo "PostgreSQL not ready yet, retrying..."
  sleep 2
done
echo "PostgreSQL is ready!"

# Check if the dump file exists
if [ ! -f "/tmp/ytbooks_dump.sql" ]; then
  echo "ERROR: Dump file not found at /tmp/ytbooks_dump.sql"
  exit 1
else
  echo "Found dump file, size: $(ls -lh /tmp/ytbooks_dump.sql | awk '{print $5}')"
fi

# Check if the database is already populated
echo "Checking if database is already populated..."
TABLES=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" -t | xargs)
echo "Found $TABLES tables in database"

if [ "$TABLES" -eq "0" ] || [ -z "$TABLES" ]; then
  echo "Initializing database with dump file..."
  
  # Use psql to import the dump file with verbose output
  echo "Starting database import..."
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -f /tmp/ytbooks_dump.sql
  
  # Verify the import
  TABLES_AFTER=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" -t | xargs)
  echo "After import: Found $TABLES_AFTER tables in database"
  
  if [ "$TABLES_AFTER" -eq "0" ]; then
    echo "ERROR: Database import failed, no tables created"
    exit 1
  else
    echo "Database initialization completed successfully."
  fi
else
  echo "Database already contains tables. Skipping initialization."
fi

# List all tables for verification
echo "Listing all tables in the database:"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"
