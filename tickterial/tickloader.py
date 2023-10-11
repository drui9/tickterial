import os
import pytz
import struct
import loguru
import requests
from typing import Tuple, List
from datetime import datetime, timedelta
from lzma import LZMADecompressor, LZMAError, FORMAT_AUTO # noqa: F401


class Tickloader():
	endpoint = "https://datafeed.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like\
		Gecko) Chrome/102.0.5005.61 Safari/537.36'
	}

	def __init__(self, db):
		self.logger = loguru.logger
		self.db = db
		self.cache = '.tick-data' # todo: relocate cache
		self.data_format = '!3i2f'
		# init requests' Session()
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
		timestr = hour.strftime("%Y-%m-%d %H")
		return f'{_cache_path}/{symbol}_{str(timestr).replace(" ","_")}'

	def decmp_lzma(self, bdata):
		"""Decompress binary compressed file"""
		# todo
		dcmp = LZMADecompressor(FORMAT_AUTO)
		return dcmp.decompress(bdata)

	def format_time_range(self, timerange: Tuple[datetime, datetime]) -> List[datetime]:
		out = list()
		# validate types
		for tm in timerange:
			if type(tm) is not datetime:
				raise TypeError(f'Time range MUST of type: {type(datetime)}')
		#
		_start, _end = min(timerange), max(timerange)
		#
		if _start == _end:
			out.append(_start)
			return out
		# increment hours with time steps
		_step = timedelta(hours=1)
		while _start < _end:
			out.append(_start)
			_start += _step
		return out

	def download(self, symbol :str, hour :datetime, utcoffset = 3):
		"""Downloads ticks for <hour>. utcoffset = utc - local (default= 3hours)"""
		timestamp = self.to_gmt(hour, utcoffset)
		if not self.is_valid_time(timestamp):
			self.logger.info(f'Invalid time {symbol}[{hour.ctime()}, utc:{timestamp.ctime()}]')  # noqa: E501
			return
		# check if cached
		self.logger.info(f'Preparing data: {symbol}[{hour.ctime()}]')
		_path = self.get_cache_path((symbol, timestamp))
		if not (_data := self.get_from_cache(_path)):
			self.logger.info(f'Fetch {symbol}[{hour.ctime()} as {timestamp.ctime()}]')
			params = {
				'currency': symbol,
				'year': timestamp.year,
				'month': timestamp.month - 1,
				'day': timestamp.day,
				'hour': timestamp.hour
			}
			try:
				url = self.endpoint.format(**params)
				res = self.requests.get(url, timeout=13, allow_redirects=False)
				if not res.ok:
					err = f'httpErrCode[{res.status_code}]'
					self.logger.critical(f'Download {symbol}:{hour.ctime} failed! {err}')  # noqa: E501
				elif not (_data := res.content):
					return
				# save to cache
				self.to_cache(_path, _data)
				self.logger.info(f'{hour} data downloaded.')
			except requests.exceptions.ConnectionError:
				self.logger.critical(f'Connection Error! {hour.ctime()}')
			except Exception as e:
				e.add_note(f'{hour.ctime()}: ticks download failed!')
				self.logger.exception(e)
				return
		#
		bdata = self.decmp_lzma(_data)
		return self.format_data(bdata, symbol, hour)

	def format_data(self, data, symbol, day):
		point = 1e5
		if symbol.lower() in ['usdrub', 'xagusd', 'xauusd']:
			point = 1e3
		#
		for data in struct.iter_unpack(self.data_format, data):
			tm, askp, bidp, askv, bidv = data
			daystamp = datetime(day.year, day.month, day.day, day.hour)
			yield {
				'timestamp': (daystamp + timedelta(milliseconds=tm)),
				'ask': askp / point,
				'bid': bidp / point,
				'ask-vol': round(askv * 1e6),
				'bid-vol': round(bidv * 1e6)
			}

	def to_cache(self, path :str, data :bytes) -> int:
		with open(path,'wb') as out:
			return out.write(data)

	def to_gmt(self, time :datetime, utcoffset :int=0) -> datetime:
		"""Converts local time to GMT with respect to utc hour offset"""
		"""Assumes gmt==utc"""
		if not utcoffset:
			return time
		return time - timedelta(hours=utcoffset)

	def is_dst(self, time: datetime) -> bool:
		locale = pytz.timezone('Etc/GMT')
		return locale.localize(time).dst() != timedelta(0)

	def is_valid_time(self, time: datetime) -> bool:
		"""Checks GMT time for forex session validity"""
		_session_start = 21
		if self.is_dst(time):
			_session_start = 22
		# filter weekends
		if time.weekday() <= 3:
			return True
		elif time.weekday() == 4:
			if time.hour <= _session_start:
				return True
		elif time.weekday() == 6:
			if time.hour >= _session_start:
				return True
		return False
