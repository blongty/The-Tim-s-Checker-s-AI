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
    return 'interval'

async def computation():
    while TIME != TIMERFLAGS.TOO_LONG:
        await asyncio.sleep(1)
        print('calculating...', flush=True)
    return 'computation'

async def test():
    global TIME
    inter = asyncio.Task(interval(5))
    comp = asyncio.Task(computation())
    a = await asyncio.gather(inter, comp)
    #print('returning values a =', a[0], 'b =', a[1], flush=True)


print('before async run', flush=True)
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
print('after async run', flush=True)