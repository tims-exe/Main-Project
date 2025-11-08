from .core.redis_client import RedisClient

def main():
    print("Starting Senticore Engine...")
    print("Reading from Queue")

    client = RedisClient()
    stream_name = "job"

    try:
        while True:
            messages = client.read_stream(stream_name)

            for message_id, message_data in messages:
                print(f"{message_id} : {message_data}")
    
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    
    finally:
        client.close()
        print("Service stopped.")


if __name__ == "__main__":
    main()
