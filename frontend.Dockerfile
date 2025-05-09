# Use Node.js as the base image
FROM node:20-alpine

# Set working directory
WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Expose the port Vite runs on
EXPOSE 3000

# Start Vite development server with host set to 0.0.0.0 to allow external access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
