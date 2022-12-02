import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('collection', type=Path)
args = parser.parse_args()

with args.collection.open() as f:
    data = json.load(f)

with args.collection.with_suffix('.ndjson').open('w') as f:
    json.dump(data, f)
