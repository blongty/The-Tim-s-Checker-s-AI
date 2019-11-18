import asyncio
from enum import Enum
import time

MAX_TIME = 0  # Set to 8 minnutes

class TIMERFLAGS(Enum):
    HAS_TIME = 0
    TOO_LONG = 1

TIME = TIMERFLAGS.HAS_TIME

async def interval(t):
    global TIME
    await asyncio.sleep(t)
    TIME = TIMERFLAGS.TOO_LONG
    return

async def computation():
    while TIME != TIMERFLAGS.TOO_LONG:
        await asyncio.sleep(1)
        print('calculating...', flush=True)

async def test():
    global TIME
    await asyncio.gather(asyncio.create_task( interval(5) ), asyncio.create_task( computation() ))
    print('returning value', flush=True)

print('before async run', flush=True)
asyncio.run(test())
print('after async run', flush=True)