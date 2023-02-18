FROM python:3.11

# Select working directory
WORKDIR /app

# Copy requirements.txt to working directory
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy source code to working directory
COPY __init__.py .
COPY __main__.py .
COPY api.py .
COPY modules/ ./modules/

# Create data directory
RUN mkdir -p /data/logs

# Run the application
CMD ["python3", "__main__.py"]
