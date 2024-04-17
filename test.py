from datetime import datetime
from tickterial import Tickloader


def test_download():
	tickloader = Tickloader()
	period = datetime(hour=17, day=8,month=4, year=2024)
	data = tickloader.download('GBPUSD', period)
	#
	ticks = list()
	for tick in data:
		ticks.append(tick)
	if ticks:
		print(f'{period} tick count: {len(ticks)}')
		print(ticks[0])
	else:
		print('No data!')

test_download()
print('--end--')
