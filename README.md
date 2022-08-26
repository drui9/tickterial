<p style="text-align: center;">
	<img src="./tickterial.png" alt="cover" title="logo"/>
<p>

## Download and cache tick data(material) from Dukascopy Bank SA


### NB: This is a module to be integrated with your code

# Usage
```python
import asyncio
from tickterial import DataCenter
from datetime import datetime

async def main():
    ct = DataCenter(timeout=30,use_cache=True)

    # download ticks for a single hour
    ticks = await ct.get_ticks('GBPUSD',datetime(2022,6,14,21)) # 2022-06-14 21:00
    out = struct.iter_unpack(ct.format,ticks.read())    # list of tuples
    for tick in out:
        print(tick)

    # bulk download ticks: More efficient for range downloads
    timerange = (datetime(2022,6,14),datetime(2022,6,14,8))     # 2022-06-14 00:00  to 2022-06-14 8:00
    generator = await ct.get_ticks_range('GBPUSD',timerange)

    for hour, stream in generator:
        print(f'Unpacking data for: {hour}')
        out = struct.iter_unpack(ct.format,stream.read())
        for tick in out:
            print(tick)

if __name__ == '__main__':
    asyncio.run(main())
```
