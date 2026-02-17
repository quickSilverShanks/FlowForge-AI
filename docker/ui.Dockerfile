FROM python:3.10-slim

WORKDIR /flowforge

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app /flowforge/app

# Expose port
EXPOSE 8501

# Add /flowforge to PYTHONPATH so that 'app' module can be found
ENV PYTHONPATH="${PYTHONPATH}:/flowforge"

# Command to run Streamlit
CMD ["streamlit", "run", "app/ui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
