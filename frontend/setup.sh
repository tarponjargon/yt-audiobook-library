#!/bin/bash

# Update package lists
apt-get update

# Install curl and other dependencies
apt-get install -y curl

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Verify installation
node -v
npm -v

# Install frontend dependencies
cd /app/frontend
npm install

echo "Setup complete! You can now run 'npm run dev' in the frontend directory."
