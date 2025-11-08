from core.redis_client import RedisClient

def main():
    print("\n=================================")
    print("Starting Senticore Engine...")
    print("===================================\n")
    print("Reading from Queue\n")

    client = RedisClient()
    stream_name = "job"

    try:
        while True:
            messages = client.read_stream(stream_name)

            for message_id, message_data in messages:
                print(f"{message_id} : {message_data}")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    finally:
        client.close()
        print("Service stopped.")


if __name__ == "__main__":
    main()
