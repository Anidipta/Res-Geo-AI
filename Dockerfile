FROM python:3.11-slim

# Install system packages required by OpenCV / multimedia
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"]
