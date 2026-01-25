FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Copy data folder with config and users
COPY data/ ./data/

# Run the main application (which starts both bot and scheduler)
CMD ["python", "-m", "src.main"]
