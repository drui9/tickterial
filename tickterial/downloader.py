import asyncio
import aiohttp
from loguru import logger
from datetime import datetime


class TickLoader:
    url = "http://datafeed.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'}

    def __init__(self, session: aiohttp.ClientSession, timeout: int):
        self.session = session
        self.timeout = timeout

    async def _fetch(self, url: str, redirects=False):
        """executed download and catches errors if any"""
        logger.info(f'fetch: {url}')
        _data = None
        _timeout = aiohttp.client.ClientTimeout(self.timeout)
        try:
            _data = await self.session.get(url, headers=TickLoader.headers, timeout=_timeout, allow_redirects=redirects)
        except asyncio.exceptions.TimeoutError:
            logger.info(f'[request timed out] retrying: {url}')
            await asyncio.sleep(1)
            return await self._fetch(url, redirects)
        except Exception as e:
            logger.warning(str(e))
            return False, e
        ##
        if _data.status != 200:
            msg = f'{_data.status}: {url}'
            if _data.status == 302 and not redirects:
                logger.warning(f'redirected: {url}')
            else:
                logger.warning(msg)
            return False, RuntimeError(msg)
        try:
            _payload = await _data.content.read()
            return True, _payload
        except asyncio.TimeoutError as e:
            logger.warning('Asyncio timeout')
            return False, e

    def download(self, symbol: str, hour: datetime):
        """returns a coroutine which returns Tuple[(true/false), (data/error)]"""
        params = {
            'currency': symbol,
            'year': hour.year,
            'month': hour.month - 1,
            'day': hour.day,
            'hour': hour.hour
        }
        url = TickLoader.url.format(**params)
        return asyncio.create_task(self._fetch(url))
