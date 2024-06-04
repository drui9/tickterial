import sys
import argparse
from . import Ticker

# --
parser = argparse.ArgumentParser()
parser.description = '''
Download tick data from Dukascopy Bank API.
Check link for examples on how to use it through python code.

Format: <timestamp, symbol, ask, bid, ask-volume, bid-volume.
Default behavior is to stream to stdout. Pipe results to file if needed.
Source & updates: https://github.com/drui9/tickterial
'''
#
parser.add_argument('--symbols', type=str, nargs='+', required=True, help='Symbol to download')
parser.add_argument('--start', type=str, required=True, help='Valid python time str')
parser.add_argument('--end', type=str, help='Defaults to --start, single hour download')
parser.add_argument('--progress', type=str, default='false', help='Show progress bar')
parser.add_argument('--cachedir', type=str, default='.tick-data', help='Download cache directory')
parser.add_argument('--header', type=str, default='true', help='Output headers')
parser.add_argument('--print', type=str, default='true', help='Print to stdout')

# -- start
def main():
    Ticker(parser.parse_args())
    sys.stdout.flush()
    sys.exit(0)

