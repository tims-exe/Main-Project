import redis
import json
from typing import List, Tuple

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.last_id = "$"

    def read_stream(self, stream_name: str, block: int = 1000) -> List[Tuple[str, dict]]:
        try:
            messages = self.client.xread(
                {stream_name: self.last_id},
                block=block,
                count=10
            )

            if not messages:
                return []

            stream_data = messages[0][1]

            if stream_data:
                self.last_id = stream_data[-1][0]

            return stream_data

        except redis.RedisError as e:
            print(f"Redis stream error: {e}")
            return []

    def publish_ack(self, channel: str, payload: dict) -> None:
        try:
            self.client.publish(channel, json.dumps(payload))
            print(f"Published ACK to '{channel}': {payload}")
        except redis.RedisError as e:
            print(f"Redis publish error: {e}")

    def clear_stream(self, stream_name: str) -> None:
        try:
            self.client.delete(stream_name)
            self.last_id = "$"
            print(f"Cleared stream: {stream_name}")
        except redis.RedisError as e:
            print(f"Error clearing stream {stream_name}: {e}")

    def close(self):
        self.client.close()
