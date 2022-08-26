import os, lzma, pytz
from io import BytesIO
import aiohttp, asyncio
from loguru import logger
from typing import List, Tuple
from tickterial.downloader import TickLoader
from datetime import datetime, timedelta


class DataCenter:
    def __init__(self, timeout: int = 30,fail_on_count: int = 3, use_cache: bool = True):
        self.path = '.cache'
        self.format = '!3i2f'
        self.use_cache = use_cache
        self.timeout = timeout
        self.fail_count = fail_on_count
        self.initialize()

    def initialize(self) -> None:
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        return

    def _generate_path(self, props: Tuple[str,datetime]) -> str:
         symbol , hour = props
         _cache_path = f'{self.path}/{symbol}'
         if not os.path.exists(_cache_path):
             os.mkdir(_cache_path)
         return f'{_cache_path}/{symbol}_{str(hour).replace(" ","_")}'

    def _from_cache(self, path: str) -> Tuple[bool, bytes]:
        if not os.path.isfile(path):
            return False, b''
        with open(path, 'rb') as infile:
            _data_out = infile.read()
            if not _data_out:
                return False, b''
            return True, _data_out

    def _to_cache(self, path: str, data: bytes) -> int:
        if not self.use_cache:
            return 0
        with open(path,'wb') as out:
            return out.write(data)

    def _is_dst(self, time: datetime) -> bool:
        locale = pytz.timezone('Etc/GMT')
        return locale.localize(time).dst() != timedelta(0)

    def _is_valid_time(self, time: datetime) -> bool:
        """Checks GMT time for forex session validity"""
        _session_start = 21
        if self._is_dst(time):
            logger.debug('Is dst!')
            _session_start = 22
        # filter weekends
        delta = timedelta(hours=3)
        if (time + delta).isoweekday() >= 6:
            return False
        # 
        delta = timedelta(hours=4)
        _now = datetime.now() - delta
        if time >= _now:
            logger.info('Skipping future time: {}'.format(time))
            return False
        return True

    def _to_utc(self,time: datetime) -> datetime:
        """Converts local time to GMT"""
        return time - timedelta(hours=3)

    def _get_range(self, timerange: Tuple[datetime,datetime]) -> List[datetime]:
        out = list()
        _step = timedelta(hours=1)
        _start, _end = timerange
        # check type validity
        if type(_start) != type(_end):
            raise TypeError('Different time format passed!')
        else:
            if type(_start) is not datetime:
                raise RuntimeError('Time range MUST be datetime.datetime')
        if _start > _end:
            raise RuntimeError('Invalid time_range: {}'.format(timerange))

        while _start < _end:
            out.append(_start)
            _start += _step
        return out

    def _unlzma(self, data: bytes) -> bytes:
        dec = lzma.LZMADecompressor(lzma.FORMAT_AUTO)
        return dec.decompress(data)

    async def get_ticks(self, symbol: str, _hour: datetime) -> BytesIO:
        hour = self._to_utc(_hour)
        if not self._is_valid_time(hour):
            logger.warning(f'No quotes available for selected time: {_hour}')
            return BytesIO(b'')
        # 
        _path = self._generate_path((symbol,_hour))
        _found, _data = self._from_cache(_path)
        if _found:
            return BytesIO(_data)
        # Not in cache. Download data
        async with aiohttp.ClientSession() as session:
            loader = TickLoader(session,self.timeout)
            _success, _data = await loader.download(symbol,hour)
            if not _success:
                logger.warning(f'Download failed: {symbol}:{hour}')
                return BytesIO(b'')
            _data = self._unlzma(_data)
            self._to_cache(_path,_data)
            return BytesIO(_data)

    async def get_ticks_range(self, symbol: str, trange: Tuple[datetime,datetime]) -> List[Tuple[datetime,BytesIO]]:
        out = list()
        hours = self._get_range(trange)
        async with aiohttp.ClientSession() as session:
            routines = list()
            loader = TickLoader(session,self.timeout)
            for h in hours:
                utc_h = self._to_utc(h)
                if not self._is_valid_time(utc_h):
                    continue
                _path = self._generate_path((symbol,h))
                _found, _data = self._from_cache(_path)
                if _found:
                    out.append((h, BytesIO(_data)))
                    continue
                # Not in cache. Download
                routines.append((h, loader.download(symbol,utc_h)))
            # wait for downloads to complete
            results = await asyncio.gather(*[i[1] for i in routines])
            fail_count = 0
            for _i, _payload in enumerate(results):
                h = routines[_i][0]
                _success, _data = _payload
                _path = self._generate_path((symbol,h))
                # 
                if not _success:
                    fail_count += 1
                    if fail_count > self.fail_count:
                        break
                    out.append((h,BytesIO(b'')))
                    continue
                # 
                _data = self._unlzma(_data)
                self._to_cache(_path,_data)
                out.append((h,BytesIO(_data)))
                continue
        return out
