# --- Stage 1: base image ---
FROM python:3.11-slim

# Set a working directory inside the container
WORKDIR /app

# Copy and install dependencies first (Docker layer caching —
# this layer only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY app.py .

# Tell Docker that the app listens on port 5000
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
