FROM python:3.10-slim

WORKDIR /flowforge

# Install system dependencies (e.g., for lightgbm, shap)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (ensure 'app' module structure)
COPY app /flowforge/app

# Expose port
EXPOSE 8000

# Command to run the backend (from parent directory so 'app' is importable)
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
