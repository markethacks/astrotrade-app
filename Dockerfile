# AstroTrade Personal Assistant - Dockerfile

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p sweph outputs data

# Download Swiss Ephemeris files (optional - can be mounted as volume)
RUN cd sweph && \
    wget -q https://www.astro.com/ftp/swisseph/ephe/seas_18.se1 || true && \
    wget -q https://www.astro.com/ftp/swisseph/ephe/semo_18.se1 || true && \
    wget -q https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1 || true && \
    cd ..

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
