import json
from datetime import datetime
from tickterial import Tickloader
# GBPUSD EURUSD USDJPY XAUUSD
# --start '2024-04-08 17:00:00'
# --end '2024-04-10 00:00:00'

def test_download():
	tickloader = Tickloader()
	start = datetime(hour=17, day=8,month=4, year=2024)
	end = datetime(hour=0, day=10,month=4, year=2024)
	times = tickloader.format_time_range((start, end))
	#
	ticks = list()
	for period in times:
		if data := tickloader.download('GBPUSD', period):
			for tick in data:
				ticks.append(tick)
	if ticks:
		# dump ticks to a json file
		with open('ticks.json', 'w') as tf:
			json.dump(ticks, tf)
		# print(f'tick count: {len(ticks)}')
		# print(ticks[0])
	else:
		print('No data!')

test_download()
print('--end--')

