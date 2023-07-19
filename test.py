#!./venv/bin/python
import requests
from datetime import datetime, timedelta
from tickterial import tickloader

def test_stream():
	with requests.Session() as session:
		headers = {'Content-Type': 'text/event-stream'}
		res = session.get('http://localhost:5050', headers=headers)
		if res.ok:
			for data in res.iter_lines():
				print(data.decode('utf8'))

def test_download():
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

test_download()
print('--end--')
