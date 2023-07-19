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
	start = datetime(hour=4, day=18,month=7, year=2023)
	end = datetime(day=19, month=7, year=2023)
	trange = tickloader.format_time_range((start, end))
	with open('xauusd.csv', 'w') as ofile:
		ofile.write('time,ask,bid\n')
		for thetime in trange:
			data = tickloader.download('XAUUSD', thetime)
			for tick in data:
				ofile.write(f"{tick['timestamp']},{tick['ask']},{tick['bid']}\n")

def test_download():
	period = datetime(hour=0, day=31,month=7, year=2023)
	data = tickloader.download('GBPUSD', period)
	#
	with open('gbpusd.csv', 'w') as ofile:
		ofile.write('time,ask,bid\n')
		for tick in data:
			ofile.write(f"{tick['timestamp']},{tick['ask']},{tick['bid']}\n")

test_download()
# test_bulk_download()
print('--end--')
