from __future__ import annotations
import asyncio
import random

async def backoff_retry(base: float = 0.5, factor: float = 2.0, max_delay: float = 20.0, attempt: int = 0) -> None:
    delay = min(max_delay, base * (factor ** attempt))
    delay = delay * (0.8 + random.random() * 0.4)  # jitter
    await asyncio.sleep(delay)
