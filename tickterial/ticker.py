import signal
from loguru import logger
from datetime import datetime
from tickterial import Tickloader
from threading import Event, Thread
from alive_progress import alive_bar
from contextlib import contextmanager

# --
class Ticker:
    def __init__(self, args):
        self.symbols = list(set(args.symbols))
        self.start = datetime.fromisoformat(args.start)
        self.end = datetime.fromisoformat(args.end) if args.end else self.start
        self.progress = args.progress
        self.cachedir = args.cachedir
        self.header = args.header
        # todo: specify log-file
        logger.disable('tickterial')
        # --
        self.terminate = Event()
        self.tickloader = Tickloader(pack=False, cachedir=self.cachedir)
        # --
        self.downloads = {
            'go': Event(),
            'data': dict()
        }
        # --set shutdown trigger
        signal.signal(signal.SIGINT, self.shutdown)
        with self.runner():
            self.run()

    @contextmanager
    def runner(self):
        # --
        streamer = Thread(target=self.tickstream)
        streamer.name = 'Streamer'
        streamer.daemon = True
        streamer.start()
        yield
        self.shutdown()

    def run(self):
        tm = (self.start, self.end)
        times = self.tickloader.format_time_range(tm)
        for symbol in self.symbols:
            if not self.downloads['data'].get(symbol):
                self.downloads['data'][symbol] = list()
            for timeframe in times:
                self.downloads['data'][symbol].append({
                    'time': timeframe,
                    'ticks': list()
                })
        # download ticks
        with alive_bar(len(self.symbols) * len(times), title='Tick download', disable=self.progress) as bar:
            for symbol, tf in self.downloads['data'].items():
                for data in tf:
                    try:
                        data['ticks'] = [i for i in self.tickloader.download(symbol, data['time']) or list()]
                    except Exception:
                        data['ticks'] = list()
                        pass # ignore errors
                    bar()
        self.downloads['go'].set()
        self.terminate.wait()

    def tickstream(self):
        self.downloads['go'].wait()
        if self.terminate.is_set():
            return
        # -- init tick stack
        symbols = list(self.downloads['data'].keys())
        time_index = 0
        ticks = dict()
        done = False
        total = 0
        while not done:
            if self.terminate.is_set():
                break
            # --
            for sym in symbols:
                total = max(total, len(self.downloads['data'][sym]))
                # accummulate ticks for symbol
                for tk in self.downloads['data'][sym][time_index]['ticks']:
                    if 'timestamp' in tk:
                        ts = tk.pop('timestamp')
                        thetick = {'symbol': sym} | tk
                        if ts in ticks:
                            if not isinstance(ticks[ts], list):
                                ticks[ts] = [ticks[ts]]
                            ticks[ts].append(thetick)
                        else:
                            ticks[ts] = thetick
            # --
            time_index += 1
            if time_index > total - 1:
                done = True
        # order streams
        out = list()
        init = True
        order = sorted(ticks)
        for i in order:
            if init:
                header = ['timestamp']
                df = ticks[i][-1].keys() if isinstance(ticks[i], list) else ticks[i].keys()
                header.extend(list(df))
                init = False
                print(','.join(header))
            # print ticks
            if isinstance(ticks[i], list):
                for tk in ticks[i]:
                    for _, v in ({'ts': i}|tk).items():
                        out.append(str(v))
            else:
                for _, v in ({'ts': i}|ticks[i]).items():
                    out.append(str(v))
            print(','.join(out))
            out.clear()
        self.terminate.set()

    def shutdown(self, *_):
        self.terminate.set()
        self.downloads['go'].set()

