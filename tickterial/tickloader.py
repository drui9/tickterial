import os
import lzma
import pytz
import struct
import loguru
import requests
import threading
from typing import Tuple, List
from datetime import datetime, timedelta


class Tickloader():
	endpoint = "https://datafeed.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

	def __init__(self, db):
		self.logger = loguru.logger
		self.db = db
		self.cache = '.tick-data'
		self.data_format = '!3i2f'
		self.dec = lzma.LZMADecompressor(lzma.FORMAT_AUTO).decompress #self.dec(data)
		# prepare requests session
		self.requests = requests.Session()
		self.requests.headers.update(self.headers)
		#
		if not os.path.exists(self.cache):
			os.mkdir(self.cache)
		return

	def get_from_cache(self, path :str) -> bytes:
		if not os.path.isfile(path):
			return b''
		with open(path, 'rb') as infile:
			_data_out = infile.read()
		return _data_out

	def get_cache_path(self, props :Tuple[str, datetime]) -> str:
		symbol , hour = props
		_cache_path = f'{self.cache}/{symbol}'
		if not os.path.exists(_cache_path):
			os.mkdir(_cache_path)
		return f'{_cache_path}/{symbol}_{str(hour).replace(" ","_")}'

	def format_time_range(self, timerange: Tuple[datetime,datetime]) -> List[datetime]:
		out = list()
		_start, _end = timerange
		# check type validity
		if type(_start) != type(_end):
			raise TypeError('Formats: start != end')
		else:
			if type(_start) is not datetime:
				raise RuntimeError(f'Time range MUST of <{type(datetime)}>')
		if _start > _end:
			raise RuntimeError(f'Error: start > end : {timerange}')
		# increment hours with time steps
		_step = timedelta(hours=1)
		while _start < _end:
			out.append(_start)
			_start += _step
		return out

	def download(self, symbol :str, timestamp :datetime, local_utc_hr_diff = 3):
		timestamp = self.to_utc(timestamp, local_utc_hr_diff)
		if not self.is_valid_time(timestamp):
			self.logger.info(f'Skipping invalid time : {timestamp}UTC')
			return None
		# check if cached
		_path = self.get_cache_path((symbol, timestamp))
		if not (_data := self.get_from_cache(_path)):
			params = {
				'currency': symbol,
				'year': timestamp.year,
				'month': timestamp.month - 1,
				'day': timestamp.day,
				'hour': timestamp.hour
			}
			url = self.endpoint.format(**params)
			self.logger.debug(url)
			try:
				res = self.requests.get(url, timeout=10)
				if not res.ok:
					self.logger.critical(f'Get {url} failed: {res.status_code}')
				_data = res.content
				if not _data:
					return None
				# save to cache
				self.to_cache(_path, _data)
			except Exception as e:
				self.logger.critical(str(e))
				return None
		return self.dec(_data)

	def to_cache(self, path :str, data :bytes) -> int:
		with open(path,'wb') as out:
			return out.write(data)

	def to_utc(self, time :datetime, local_utc_hr_diff :int) -> datetime:
		"""Converts local time to GMT"""
		return time - timedelta(hours=local_utc_hr_diff)

	def is_dst(self, time: datetime) -> bool:
		locale = pytz.timezone('Etc/GMT')
		return locale.localize(time).dst() != timedelta(0)

	def is_valid_time(self, time: datetime) -> bool:
		"""Checks GMT time for forex session validity"""
		_session_start = 21
		if self.is_dst(time):
			_session_start = 22
		# filter weekends
		delta = timedelta(hours=3)
		if (time + delta).isoweekday() >= 6:
			return False
		# 
		delta = timedelta(hours=4)
		_now = datetime.now() - delta
		if time >= _now:
			return False
		return True
