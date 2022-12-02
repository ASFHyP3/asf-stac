import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('collection', type=Path)
args = parser.parse_args()

with args.collection.open() as f:
    data = f.read().replace('\n', '') + '\n'

with args.collection.with_suffix('.ndjson').open('w') as f:
    f.write(data)
