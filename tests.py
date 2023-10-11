import requests
from datetime import datetime
from tickterial import tickloader

def test_stream():
	with requests.Session() as session:
		headers = {'Content-Type': 'text/event-stream'}
		res = session.get('http://localhost:5050', headers=headers)
		if res.ok:
			for data in res.iter_lines():
				print(data.decode('utf8'))

def test_bulk_download():
	start = datetime(day=19,month=7, year=2023)
	end = datetime(hour=2, day=20, month=7, year=2023)
	trange = tickloader.format_time_range((start, end))
	for thetime in trange:
		ticks = list()
		data = tickloader.download('XAUUSD', thetime)
		for tick in data:
			ticks.append(tick)
		if ticks:
			print(f'{thetime} tick count: {len(ticks)}')

def test_download():
	period = datetime(hour=0, day=31,month=7, year=2023)
	data = tickloader.download('GBPUSD', period)
	#
	ticks = list()
	for tick in data:
		ticks.append(tick)
	if ticks:
		print(f'{period} tick count: {len(ticks)}')
	else:
		print('No data!')

test_download()
# test_bulk_download()
print('--end--')
