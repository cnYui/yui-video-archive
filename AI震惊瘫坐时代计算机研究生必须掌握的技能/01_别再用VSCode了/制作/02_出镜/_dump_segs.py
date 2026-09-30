import json, sys
from pathlib import Path
base = Path(__file__).parent / 'asr'
ids = sys.argv[1:] or ['0176','0177','0178','0179','0181','0182','0183','0185','0187']
for f in ids:
    d = json.loads((base / f'{f}.json').read_text(encoding='utf-8'))
    print(f'=== {f} ({d["duration"]:.2f}s) ===')
    for s in d['segments']:
        print(f'  {s["start"]:.2f}-{s["end"]:.2f}: {s["text"]}')
