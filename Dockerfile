FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY requirements.txt .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV KASPA_RPC_URL=http://23.111.147.178:16110

# Expose port (not needed for stdio but good for documentation)
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "src.main"]