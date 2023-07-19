#!./venv/bin/python
import requests
from datetime import datetime, timedelta
from tickterial import tickloader

def stream():
	with requests.Session() as session:
		headers = {'Content-Type': 'text/event-stream'}
		res = session.get('http://localhost:5050', headers=headers)
		if res.ok:
			for data in res.iter_lines():
				print(data.decode('utf8'))

def download():
	period = datetime(year=2023, month=7, day=10, hour=19)

	data = tickloader.download('GBPUSD', period)
	# print(data)

download()
print('--end--')
