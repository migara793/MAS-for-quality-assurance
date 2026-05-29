# Use a Python base image with Node.js support
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Pre-install MCP servers globally with retries
RUN for i in 1 2 3 4 5; do \
    npm install -g @modelcontextprotocol/server-filesystem \
    mcp-shell \
    @playwright/mcp \
    @modelcontextprotocol/server-github \
    --unsafe-perm && break || \
    (echo "Global npm install failed, retrying in 15s... (\$i/5)" && sleep 15); \
    done

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt package.json package-lock.json* ./

# Install Python dependencies
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 -r requirements.txt

# Install Playwright system dependencies
RUN playwright install-deps chromium

# Install Playwright browsers with retries to handle transient network/DNS issues
RUN for i in 1 2 3 4 5; do \
    playwright install chromium && break || \
    (echo "Playwright install failed, retrying in 15s... (\$i/5)" && sleep 15); \
    done

# Install Node.js dependencies with retries to handle transient network issues
RUN for i in 1 2 3 4 5; do \
    npm install --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && break || \
    (echo "npm install failed, retrying in 15s... (\$i/5)" && sleep 15); \
    done

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/usr/local/bin:${PATH}"

# Make startup script executable
RUN chmod +x start.sh

# Run the startup script
CMD ["./start.sh"]
