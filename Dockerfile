# Use the official Python 3.12 image as the base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    libnss3 libnspr4 libatk1.0-0 libatspi2.0-0 \
    libxcomposite1 libxdamage1 nss-plugin-pem ca-certificates zstd libzstd-dev \
    libatk-bridge2.0-0\
    libcups2\
    libxfixes3\
    libxrandr2\
    libgbm1\
    libxkbcommon0\
    libpango-1.0-0\
    libcairo2\
    libasound2\
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# installs the chromium browser, necessary for Playwright
RUN python -m playwright install chromium

# Copy the application code
# COPY . .

# Copy the wait script
COPY wait_for_postgres.py .

# Expose the ports Flask and Adminer run on
EXPOSE 5000
EXPOSE 8080

# Define the default command to wait for Postgres, initialize the DB via Flask CLI, and then run the app
# CMD ["sh", "-c", "python wait_for_postgres.py && flask init-db && flask run --host=0.0.0.0"]
CMD ["sh", "-c", "python wait_for_postgres.py && flask run --host=0.0.0.0"]
