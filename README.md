<p style="text-align: center;">
	<img src="https://raw.githubusercontent.com/sp3rtah/tickterial/master/tickterial.png" alt="cover" title="tickterial logo"/>
<p>

## Download and cache tick data(material) from Dukascopy Bank SA
This is a local API server that downloads tick data on request and caches results for subsequent calls. Finally, a free historical data collection for backtesting your forex trading algorithms!
All instruments on [this page](https://www.dukascopy.com/swiss/english/marketwatch/historical/) are supported! (But only `currency pairs` are tested based on my use case.).  <a href="mailto:ngaira14nelson@gmail.com">Email me</a> for special requests.

## Installation ::Python3
```pip install tickterial```

## Usage
This module can be used in two modes. As an API server using a `flask` backend, and as a module.

## `Module usage`
```python
from datetime import datetime, timedelta
from tickterial import tickloader

def download():
	period = datetime.now() - timedelta(minutes=60) # previous hour
	data = tickloader.download('GBPUSD', period)
	#
	count = 4
	for index, tick in enumerate(data):
		print(tick)
		#
		count -= 1
		if not count:
			print(f'--showing first {index + 1} ticks--')
			break

download()
print('--end--')
```

## `Sample output from GBPUSD`
`{'timestamp': 1689631196.875, 'ask': 1.30788, 'bid': 1.30778, 'ask-vol': 900000, 'bid-vol': 900000}`


## `API-mode usage`
`Coming soon...`

## TODO
- Internally convert prices to float 																	- DONE
- Add database caching for large offline histories
- Add API functionality for use as a local tcp streaming service
- Containerize the API through docker for ease of use
- Stick around. There's more coming!

## Notes
- Cache is store in UTC. Pass your UTC time difference as last parameter to `tickloader.download` to fix local time offset.
- Tick data can only be fetch to the previous hour. Current hour returns 404. This is handled internally though
- Cache is stored in current working directory, path = `.tick-data`. Move this directory when migrating your server to save bandwidth and keep your cached data, or mount a local directory when using docker volumes.

## `Please donate to keep development going`
- My Public Address to Receive BTC: `bc1qg8tqa0azl7el38wtdfawxnj2tfz46ajtjnv685`
- Via [Trust Wallet](https://link.trustwallet.com/send?coin=0&address=bc1qg8tqa0azl7el38wtdfawxnj2tfz46ajtjnv685)
