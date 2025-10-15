FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/lAmeR1/py-kaspad-client.git

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY requirements.txt .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (not needed for stdio but good for documentation)
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "src.main"]