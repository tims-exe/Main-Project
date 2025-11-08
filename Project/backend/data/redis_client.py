import os
import json
import asyncio
from typing import Optional, Dict, Any
import redis.asyncio as redis
from redis.asyncio import Redis


class RedisClient:
    def __init__(self):
        self.client: Optional[Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.responses: Dict[str, asyncio.Future] = {}
        self._running = False
        self._listener_task: Optional[asyncio.Task] = None

    async def connect(self):
        if self.client is None:
            self.client = await redis.from_url(
                self.redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            print(f"Connected to Redis at {self.redis_url}")
            
            # Start listener in background
            self._running = True
            self._listener_task = asyncio.create_task(self._listen_loop())

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

    async def send_to_engine(self, request_id: str, data: Dict[str, Any]) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")

        message_data = {
            "request_id": request_id,
            "data": json.dumps(data)
        }

        await self.client.xadd("job", message_data)
        print(f"Sent request to engine: {request_id}")

    async def wait_for_response(self, request_id: str, timeout: float = 5.0) -> Dict[str, Any]:
        # Create a future for this request
        future = asyncio.Future()
        self.responses[request_id] = future
        
        try:
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            # Clean up if timeout occurs
            if request_id in self.responses:
                del self.responses[request_id]
            raise TimeoutError(f"No response received for request {request_id}")

    async def _listen_loop(self):
        last_id = "$"  

        while self._running:
            try:
                # Read from ack stream
                response = await self.client.xread(
                    streams={"ack": last_id},
                    block=1000, 
                    count=10
                )

                if not response:
                    continue

                # Process messages
                for stream_name, messages in response:
                    for message_id, message_data in messages:
                        # Update last_id to continue from this point
                        last_id = message_id
                        
                        # Get request_id from message
                        request_id = message_data.get("request_id")
                        
                        if request_id and request_id in self.responses:
                            future = self.responses[request_id]
                            
                            # Set the result if future is still pending
                            if not future.done():
                                future.set_result(message_data)
                            
                            # Clean up
                            del self.responses[request_id]

            except asyncio.CancelledError:
                print("Redis listener cancelled")
                break
            except Exception as e:
                print(f"Error in Redis listener: {e}")
                await asyncio.sleep(1)


# Global instance
redis_client = RedisClient()
