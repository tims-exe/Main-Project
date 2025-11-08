import redis
import time 
from typing import Optional

class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host = host,
            port = port, 
            db = db, 
            decode_responses= True
        )
        self.last_id = "$"

    def read_stream(self, stream_name: str, block: int = 1000) -> list:
        try: 
            messages = self.client.xread(
                {stream_name: self.last_id},
                block=block,
                count=10
            )

            if messages:
                stream_data = messages[0][1]
                if stream_data:
                    self.last_id = stream_data[-1][0]
                return stream_data

            return []
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return []
    
    def close(self):
        self.client.close()