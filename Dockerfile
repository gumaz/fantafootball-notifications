FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Copy config and users files
COPY data/config.json ./data/config.json
COPY data/users.json ./data/users.json

# Run the main application (which starts both bot and scheduler)
CMD ["python", "-m", "src.main"]
