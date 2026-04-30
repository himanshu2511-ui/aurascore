FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required by MediaPipe and OpenCV
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start the FastAPI application. Render passes the PORT env variable automatically.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
