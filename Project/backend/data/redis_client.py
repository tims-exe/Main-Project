import os
import json
import asyncio
from typing import Optional, Dict, Any
import redis.asyncio as redis
from redis.asyncio import Redis
from ..chat.models import JobMsgType


class RedisClient:
    def __init__(self):
        self.client: Optional[Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        self.responses: Dict[str, asyncio.Future] = {}
        self._listener_task: Optional[asyncio.Task] = None
        self._running = False

        self.ACK_CHANNEL = "ack_channel"

    async def connect(self):
        if self.client is None:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            print(f"Connected to Redis at {self.redis_url}")

            self._running = True
            self._listener_task = asyncio.create_task(self._pubsub_listener())

    async def disconnect(self):
        self._running = False

        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self.client:
            await self.client.close()
            print("Disconnected from Redis")

    async def send_to_engine(self, request_id: str, data: JobMsgType) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")

        payload = {
            "request_id": request_id,
            "data": data.model_dump_json()
        }

        await self.client.xadd("job", payload)
        print(f"Sent job → stream: {request_id}")

    async def wait_for_response(self, request_id: str, timeout: float = 300 ) -> Dict[str, Any]:
        future = asyncio.get_running_loop().create_future()
        self.responses[request_id] = future

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            # cleanup
            self.responses.pop(request_id, None)

            return {
                "request_id": request_id,
                "message": "Error processing your message"
            }

    async def _pubsub_listener(self):
        pubsub = self.client.pubsub()
        await pubsub.subscribe(self.ACK_CHANNEL)

        print(f"Subscribed to pubsub channel: {self.ACK_CHANNEL}")

        try:
            async for msg in pubsub.listen():
                if not self._running:
                    break

                if msg["type"] != "message":
                    continue

                try:
                    data = json.loads(msg["data"])
                    request_id = data.get("request_id")

                    if request_id and request_id in self.responses:
                        future = self.responses.pop(request_id)

                        if not future.done():
                            future.set_result(data)

                except Exception as e:
                    print(f"Error handling pubsub message: {e}")

        except asyncio.CancelledError:
            print("PubSub listener cancelled")
        finally:
            await pubsub.unsubscribe(self.ACK_CHANNEL)
            await pubsub.close()


# Global instance
redis_client = RedisClient()
