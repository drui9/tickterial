import argparse

# --
parser = argparse.ArgumentParser()
#
parser.add_argument('symbol', type=str, help='Symbol to download')
parser.add_argument('from', type=str, help='Tick download start date')
parser.add_argument('to', type=str, help='Tick download end date')

# -- todo: parse commandline arguments
def main():
    args = parser.parse_args()
    raise NotImplementedError(args)
