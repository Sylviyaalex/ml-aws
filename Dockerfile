# Python slim base
FROM python:3.11-slim

# Prevents Python from writing .pyc files & buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (build tools for scikit-learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt

# Copy the rest
COPY . .

# Expose FastAPI port
EXPOSE 8080

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
