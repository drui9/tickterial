<p style="text-align: center;">
	<img src="https://raw.githubusercontent.com/sp3rtah/tickterial/master/tickterial.png" alt="cover" title="tickterial logo"/>
<p>

# tickterial: forex & cfd tick data
Download and cache tick data from Dukascopy Bank SA.

## Installation ::Python3
- `pip install tickterial`
- `tickterial -h` to check supported arguments.

Example multi-symbol stream download:
```monospace
$ tickterial --symbols GBPUSD EURUSD USDJPY XAUUSD --start '2024-04-08 17:00:00' --end '2024-04-10 00:00:00' --progress true

# Output format is: <timestamp, symbol, ask, bid, ask-volume, bid-volume>,[repeated if multiple symbols at same timestamp]
...
timestamp, symbol, ask-price, bid-price, ask-volume, bid-volume
1712696398.152,GBPUSD,1.26785,1.26774,900000,900000
1712696398.192,USDJPY,1.51808,1.51759,1800000,1800000
1712696398.295,XAUUSD,2353.505,2352.835,90,470
1712696398.343,USDJPY,1.51808,1.51755,1800000,1800000
...
#When multiple ticks exist in the same timestamp, the output is concatenated as such:
1712696267.989,EURUSD,1.0857,1.08569,990000,900000,1712696267.989,GBPUSD,1.26778,1.26769,900000,900000
...
```
- Easy, normalized prices, multi-currency, simultaneous and ordered price output!

## Why the name? <tickterial>
I thought of tick material as a replacement for tick-data, which has been used way too many times already, both in research and code.

## How does it work?
- This package downloads tick data on request and caches downloads to disk for subsequent `offline` calls. Finally, a quick and easy historical data collection for backtesting trading algorithms!
- Currency pairs(tested) and more(untested) instruments on [this page](https://www.dukascopy.com/swiss/english/marketwatch/historical/) are supported. <a href="mailto:drui9@duck.com">Email me</a> for requests.
- Note that this code respects their API rate-limits. As such, asyncronous frameworks like aiohttp largely returned errors, before I settled for a syncronous. A work-around is to use a list of proxies for each individual request (planned).

### Integrating with your code
```python
from datetime import datetime
from tickterial import Tickloader


def test_download():
	tickloader = Tickloader()
	period = datetime(hour=17, day=8,month=4, year=2024)
	print(period.ctime())
	#
	ticks = list()
	if data := tickloader.download('GBPUSD', period):
		for tick in data:
			ticks.append(tick)
		if ticks:
			print(f'{period} tick count: {len(ticks)}')
			print(ticks[0])
		else:
			print('No data!')

test_download()
print('--end--')

#output:
# {'timestamp': 1689631196.875, 'ask': 1.30788, 'bid': 1.30778, 'ask-vol': 900000, 'bid-vol': 900000}

```

## Notes
- Cache is store in UTC. Pass your UTC bias as last parameter to `tickloader.download` to fix local time offset.
- Tick data can only be fetched to the previous hour. Current hour returns 404, thus ignored.
- Cache is stored in current working directory(default), path = `$(pwd)/.tick-data`, or to path specified in --cachedir option, also available while creating `Tickterial(cachedir=/your/path)` object. Move this directory when migrating to keep your offline tick data.
- For multi-symbol downloads, the streams are ordered by timestamp(wow!). You can stream ordered prices for say EURUSD, GBPUSD etc. (Currently, only supported for commandline invokation.)
- Keeping track of the number of `,` should allow easy partitioning of the ticks for `backtesting systems`. - Voila! My next project.

## Support the project
I couldn't afford college. I therefore learn through the web and create amazing software that can impact this world in ways I can. A little help will offload my bills and give me more working time.
- You can paypal at me: `ngaira14nelson@gmail.com`
- Contact me for requests, optimizations, pull-requests and every other interesting topic.


## TODO
- Add support for streaming ordered-ticks to TCP endpoint - planned
- Support for pandas dataframes and numpy arrays - differred
- Integrate mplfinance for candlestick plotting - differred
- Use proxies to perform async downloads - planned
- Parse ticks to generate timeframe data - differred
- Port to faster languages (C/Rust/GO) - differred

```monospace
In the spirit of opensource:
	# dev.drui9
```