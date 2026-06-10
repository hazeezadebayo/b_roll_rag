FROM python:3.10-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user (good practice, though we might need root for some mounts)
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# Expose API port
EXPOSE 8000

# Default command
CMD ["uvicorn", "b_roll_rag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
