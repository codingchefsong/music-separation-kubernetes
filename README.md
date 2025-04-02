# Music Separation as a Service (MSaaS) - Kubernetes Deployment

![Music Separation](images/music_separation.png)

## Overview

**Music Separation as a Service (MSaaS)** is a cloud-based solution providing an API to automatically separate music tracks from a given MP3 file. It leverages the powerful **Demucs** deep learning model from Facebook to perform high-quality waveform source separation (vocals, drums, bass, etc.). This project is designed for scalability, reliability, and performance using **Kubernetes** for orchestration, **Redis** for task queuing, and **Min.io** as an object storage service to handle large MP3 files and their separated tracks.

## Skills Demonstrated

- **Kubernetes & Docker**: Setting up and managing containerized applications using Kubernetes.
- **Microservices Architecture**: Developing a REST API frontend and worker services to handle music separation tasks.
- **Redis Queues**: Implementing Redis queues for task management between the frontend and worker services.
- **Cloud Object Storage**: Integration with **Min.io** for storing MP3 files and separated tracks.
- **Deep Learning Integration**: Incorporating Demucs (a state-of-the-art model for waveform source separation) into the worker service.
- **Port Forwarding & Debugging**: Configuring and testing services locally with Kubernetes port forwarding.
- **Service Monitoring**: Using logging and debugging tools to monitor system health and performance.

## Architecture

The architecture consists of the following services, each deployed in individual containers and orchestrated using Kubernetes:

- **REST API Frontend (`rest`)**: Handles API requests for music analysis and manages communication between the user and the backend worker service. It queues tasks in Redis for processing.
  
- **Worker (`worker`)**: Receives queued tasks from Redis, processes MP3 files using **Demucs** for waveform source separation, and stores results in Min.io object storage.

- **Redis**: A lightweight key-value store used for managing task queues between the frontend and worker services.

- **Min.io Object Storage**: A scalable object storage system to store MP3 files and their separated tracks.

### Workflow
1. **User Uploads MP3**: The user uploads an MP3 file to the system via the REST API.
2. **Task Queued**: The `rest` frontend adds the task to a Redis queue.
3. **Processing by Worker**: A worker node retrieves the task, processes the MP3 file with Demucs to separate audio components (vocals, drums, bass, etc.).
4. **Storage**: The separated tracks are saved to Min.io with names like `<songhash>-<track>.mp3`.
5. **Track Retrieval**: The user can retrieve the separated tracks directly from Min.io.

### Cloud Object Storage
- **Min.io**: Used to store both the original MP3 files and the resulting separated audio tracks.
- Each separated track is saved with a unique name based on the song hash and track type, ensuring organized storage for easy retrieval.

![Min.io Buckets](images/buckets.png)

## Setup and Deployment

### Kubernetes Cluster

You can deploy the MSaaS system either locally using a Docker and Kubernetes setup or on **Google Kubernetes Engine (GKE)** for production. The system utilizes **Kubernetes** to manage deployments, scaling, and resource allocation across services.

### Services
1. **Redis Service**: A Redis instance is used to manage task queues between the `rest` frontend and `worker` services.
2. **Min.io Object Storage**: A Min.io server is deployed for handling object storage.
3. **Worker**: The worker service uses the **Demucs** deep learning model to perform audio source separation on the uploaded MP3 files.

### Port Forwarding for Local Development
To facilitate local development, port forwarding can be used to connect your local machine to the services running in the Kubernetes cluster. Use the following commands to forward Redis and Min.io services to local ports:
```bash
kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
kubectl port-forward --namespace minio-ns svc/myminio-proj 9000:9000 &

