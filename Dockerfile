FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        exiftool \
        ffmpeg \
        libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /server

# Copy application
COPY *.py .
COPY requirements-linux.txt .
COPY endpoints ./endpoints

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-linux.txt

CMD ["python", "main.py"]