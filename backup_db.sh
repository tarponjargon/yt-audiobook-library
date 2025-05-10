   #!/bin/bash

   docker exec yt-audiobook-library-postgres-1 pg_dump -U root ytbooks > init_data/ytbooks_dump.sql

   echo "Initialization dump updated: init_data/ytbooks_dump.sql"