import os
import json
import redis
import logging
import requests
from minio import Minio
import time

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

# MinIO configuration
MINIO_HOST = os.getenv("MINIO_HOST", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "rootuser")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "rootpass123")
REDIS_KEY_WORKER = 'toWorker'
REDIS_KEY_LOG = 'logging'

# Setup Redis and Minio clients
def create_minio_client():
    while True:
        try:
            minio_client = Minio(
                MINIO_HOST,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False
            )
            # Try to list buckets as a way to test the connection
            minio_client.list_buckets()
            print("Connected to MinIO.")
            return minio_client
        except S3Error as e:
            print(f"Connection to MinIO failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait 5 seconds before retrying
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Use the function to create the client with retry logic
minio_client = create_minio_client()

def create_redis_client():
    while True:
        try:
            redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)
            # Test the connection to ensure it's available
            redis_client.ping()
            print("Connected to Redis.")
            return redis_client
        except redis.exceptions.ConnectionError as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait 5 seconds before retrying
        except MaxRetryError as e:
            print(f"Max retry error encountered: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Use the function to create the client with retry logic
redis_client = create_redis_client()

# Log setup
logging.basicConfig(level=logging.INFO)

def log_info(message):
    redis_client.rpush(REDIS_KEY_LOG, message)

def download_song(song_key):
    filename = f"./demucs/input/{song_key}.mp3"
    minio_client.fget_object(song_key, f"{song_key}.mp3", filename)
    return filename

def separate_tracks(song_key):
    # print("================================================================")
    # original_dir = os.getcwd()
    # os.chdir("demucs")
    # os.system(f"make run track={song_key}.mp3 mp3output=true")
    # os.chdir(original_dir)
    # print("================================================================")
    input_file = f"./demucs/input/{song_key}.mp3"
    output_dir = f"./demucs/output/"
    os.system(f"python3 -m demucs -d cpu --mp3 --out {output_dir} {input_file}")

def upload_tracks(song_key):
    output_dir = f"./demucs/output/htdemucs/{song_key}"
    # output_dir = f"./demucs/output/{song_key}"
    for part in ["bass", "drums", "vocals", "other"]:
        part_file = f"{output_dir}/{part}.mp3"
        print(f"{song_key}_{part}.mp3")
        minio_client.fput_object(song_key, f"{song_key}_{part}.mp3", part_file)

def main():
    while True:
        try:
            task = redis_client.blpop(REDIS_KEY_WORKER, timeout=3)
            print("Received task:", task)
            
            # Initialize song_key to avoid unbound variable issue
            song_key = None
            if task:
                try:
                    # Decode and load JSON message
                    # message = json.loads(task[1].decode('utf-8'))
                    song_key = task[1].decode('utf-8')
                    print("Parsed message:", song_key)

                    # for thing in minio_client.list_objects(MINIO_BUCKET_NAME, recursive=True):
                    #     print(thing.object_name)

                    song_file = download_song(song_key)
                    log_info(f"Downloaded song {song_key} for processing.")

                    separate_tracks(song_key)
                    log_info(f"Separated song {song_key} into tracks.")

                    upload_tracks(song_key)
                    log_info(f"Uploaded separated tracks for {song_key} to Min.io.")

                    # If there's a webhook, send a POST request
                    if "webhook" in song_key:
                        requests.post(song_key["webhook"], json={"status": "done", "song_id": song_key})

                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}. Task content: {task[1]}")
                    log_info(f"Failed to parse JSON for task: {task[1]}")
                    
                except Exception as e:
                    logging.error(f"Failed to process task: {e}")
                    if song_key:
                        log_info(f"Failed to process task for song {song_key}")
                    else:
                        log_info("Failed to process task due to missing song_key")
        except Exception as e:
            print(e)
        time.sleep(5)
if __name__ == "__main__":
    main()
