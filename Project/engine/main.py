from data.redis_client import RedisClient
from models.requests import RequestType
import json
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ACK_CHANNEL = "ack_channel"
JOB_STREAM = "job"

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_sentiment(text):
    """
    Analyze the emotional sentiment of the text using Groq API.
    Returns a short response message.
    """
    try:
        # Create chat completion with Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an emotional sentiment analysis chatbot. "
                        "Analyze the user's message and respond with a short, "
                        "empathetic message (1-2 sentences) that acknowledges "
                        "their emotional state and provides supportive feedback."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama-3.1-8b-instant",  # Fast and efficient model
            temperature=0.7,
            max_tokens=100  # Keep responses short
        )
        
        # Extract the response
        response = chat_completion.choices[0].message.content
        return response
    
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "I'm having trouble analyzing that right now. Please try again."


def main():
    print("\n=================================")
    print("Starting Senticore Engine...")
    print("=================================\n")

    client = RedisClient()

    # Clear job stream on startup
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
                        # Use Groq API to analyze sentiment
                        ai_response = analyze_sentiment(data.data)
                        
                        response = {
                            "request_id": request.request_id,
                            "type": "text",
                            "message": ai_response
                        }
                    else:
                        response = {
                            "request_id": request.request_id,
                            "error": "invalid request"
                        }

                    print("Request Received:", message_id)
                    print("User:", data.user_id)
                    print("Message:", data.data)
                    print("AI Response:", response.get("message", "N/A"))
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