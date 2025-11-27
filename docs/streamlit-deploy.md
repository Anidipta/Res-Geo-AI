# Streamlit Deployment (Docker / Streamlit Cloud)

If you need system libraries (for example `ffmpeg`, `libsm6`, `libxext6`, or OpenGL libs) when running the app on a containerized platform or on Streamlit Cloud, install them at the OS level in a `Dockerfile` rather than putting them in `requirements.txt`.

## Example Dockerfile (minimal)

```dockerfile
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
```

## Notes

- Remove OS-level packages (like `libsm6`, `libxext6`, `libgl1-mesa-glx`, etc.) from `requirements.txt` — those are not PyPI packages and will make `pip install -r requirements.txt` fail.
- If you deploy to Streamlit Cloud, push this `Dockerfile` to the repo and configure Streamlit to build using it; the apt-get line will run during the image build.

## Suggested `requirements.txt` (pip-only)

```
streamlit
folium
streamlit-folium
geopandas
pillow
numpy
kagglehub
ultralytics
transformers
requests
scikit-learn
opencv-python
```

## Local setup helper (optional)

You can create a small `setup.sh` that runs the apt-get line and then installs Python deps for local development:

```bash
#!/usr/bin/env bash
set -e
sudo apt-get update
sudo apt-get install -y ffmpeg libsm6 libxext6
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
