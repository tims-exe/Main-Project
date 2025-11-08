import os
import json
from typing import Optional, Dict, Any
import redis.asyncio as redis
from redis.asyncio import Redis


class RedisClient:
    def __init__(self):
        self.client: Optional[Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    async def connect(self):
        if self.client is None:
            self.client = await redis.from_url(
                self.redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            print(f"Connected to Redis at {self.redis_url}")

    async def disconnect(self):
        if self.client:
            await self.client.close()
            print("Disconnected from Redis")

    async def send_to_engine(self, request_id: str, data: Dict[str, Any]) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")

        message_data = {
            "request_id": request_id,
            "data": json.dumps(data)
        }

        await self.client.xadd("job", message_data)
        print(f"Sent request to engine: {request_id}")


    # async def listen_loop(self):

    #     while self._running:
    #         try:
    #             response = await self.client.xread(
    #                 streams = {"engine": "$"},
    #                 block = 5000
    #             )

    #             if not response:
    #                 continue

    #             for stream_name, message in response:
    #                 for message_id, message_data in message:
    #                     if "engine_update" in message_data:
    #                         await self.handle_engine_update(message_data["engine_update"])

    #         except asyncio.CancelledError:
    #             print("Redis listener Cancelled")
    #             break 
            
    #         except Exception as e:
    #             print(f"Error in Redis listener : {e}")
    #             await asyncio.sleep(1)


    
    # async def handle_engine_update(self, engine_update_json: str) :
    #     try:
    #         data = json.loads(engine_update_json)
    #         request_id = data.get("id")

    #         if request_id and request_id in self.responses:
    #             future = self.responses[request_id]
    #             if not future.done():
    #                 future.set_result(data)

    #             del self.responses[request_id]

    #     except json.JSONDecodeError as e:
    #         print(f"Failed to parse engine update : {e}")



# Global instance
redis_client = RedisClient()
