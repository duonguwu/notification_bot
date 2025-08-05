# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY notification/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY notification/ /app/

# Create upload directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "main.py"] 