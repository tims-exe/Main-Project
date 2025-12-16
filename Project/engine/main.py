from data.redis_client import RedisClient
from models.requests import RequestType
import json

ACK_CHANNEL = "ack_channel"
JOB_STREAM = "job"

def main():
    print("\n=================================")
    print("Starting Senticore Engine...")
    print("=================================\n")

    client = RedisClient()

    # clear job stream on startup
    client.clear_stream(JOB_STREAM)

    try:
        while True:
            messages = client.read_stream(JOB_STREAM)

            for message_id, message_data in messages:
                try:
                    # Parse JSON payload
                    if isinstance(message_data.get("data"), str):
                        message_data["data"] = json.loads(message_data["data"])

                    request = RequestType(**message_data)
                    data = request.data

                    # Process request
                    if data.type == "audio":
                        response = {
                            "request_id": request.request_id,
                            "type": "audio",
                            "message": "processed"
                        }
                    elif data.type == "text":
                        response = {
                            "request_id": request.request_id,
                            "type": "text",
                            "message": data.data
                        }
                    else:
                        response = {
                            "request_id": request.request_id,
                            "error": "invalid request"
                        }

                    print("Request Received:", message_id)
                    print("User:", data.user_id)
                    print("Message:", data.data)
                    print("-" * 40)

                    # Publish response via Pub/Sub
                    client.publish_ack(ACK_CHANNEL, response)

                except Exception as e:
                    print(f"Error processing message: {e}")
                    print("Raw message:", message_data)

    except KeyboardInterrupt:
        print("\nShutting down...")

    finally:
        client.close()
        print("Service stopped.")


if __name__ == "__main__":
    main()
