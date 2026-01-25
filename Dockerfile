FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Copy example config and create data directory
COPY config.example.json ./data/config.json
RUN mkdir -p data

# Declare data directory as a volume for persistent storage
VOLUME ["/app/data"]

# Run the main application (which starts both bot and scheduler)
CMD ["python", "-m", "src.main"]
