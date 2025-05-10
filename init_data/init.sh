   #!/bin/bash

   set -e

   # Check if the database is already populated
   RECORD_COUNT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM audiobooks;" 2>/dev/null || echo "0")

   # If the database is empty, import the dump
   if [ "$RECORD_COUNT" = "0" ] || [ "$RECORD_COUNT" = " 0" ]; then
     echo "Initializing database with seed data..."
     psql -U "$DB_USER" -d "$DB_NAME" < /docker-entrypoint-initdb.d/ytbooks_dump.sql
     echo "Database initialization completed."
   else
     echo "Database already contains data, skipping initialization."
   fi