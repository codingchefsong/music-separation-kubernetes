# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app


# make \
# docker.io \
# libsndfile1 \
# libomp-dev \
# libgomp1 \
# Install dependencies and system libraries needed by PyTorch
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    ffmpeg \
    git \
    libgomp1 \
    libsndfile1 \
    libomp-dev \
    && apt-get clean
    
# Copy the current directory contents into the container at /app
COPY . /app

# Install the required Python packages
RUN pip3 install -r requirements.txt

COPY . /demucs

# Command to run the Flask application
CMD ["python", "worker-server.py"]