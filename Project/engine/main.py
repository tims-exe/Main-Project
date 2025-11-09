from data.redis_client import RedisClient
from models.requests import RequestType
import json

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
                try:
                    if isinstance(message_data.get("data"), str):
                        message_data["data"] = json.loads(message_data["data"])

                    request = RequestType(**message_data)

                    print("Request Received:", message_id)
                    print("User:", request.data.user_id)
                    print("Message:", request.data.message)
                    print()

                    client.send_ack(request.request_id, f"Acknowledgement for {request.data.message}")
                    print("-"*40)

                except Exception as e:
                    print(f"Error parsing message: {e}")
                    print("Raw message_data:", message_data)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    finally:
        client.close()
        print("Service stopped.")


if __name__ == "__main__":
    main()
