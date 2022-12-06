import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--output-file', type=Path, default='collections.ndjson')
parser.add_argument('collections', type=Path, nargs='+')
args = parser.parse_args()

with args.output_file.open('w') as output_file:
    for collection in args.collections:
        with collection.open() as f:
            data = json.load(f)
        json.dump(data, output_file)
        output_file.write('\n')
