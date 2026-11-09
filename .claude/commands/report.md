---
description: Summarise practice progress from data/results.json
allowed-tools: Bash(python3:*), Read
---

# Practice report

Summarise my mock-interview progress from `data/results.json`. This is
read-only: don't modify `data/results.json` or any other file, and don't call
the app or the OpenAI API.

## Steps

1. Compute the numbers with this script rather than by eye, so the averages
   are exact:

   ```
   python3 -c "
   import json, pathlib
   p = pathlib.Path('data/results.json')
   results = json.loads(p.read_text()) if p.exists() and p.read_text().strip() else []
   print('rounds', len(results))
   if results:
       print('avg_total', round(sum(r['total'] for r in results) / len(results), 1))
       sums, counts = {}, {}
       for r in results:
           for c in r['categories']:
               sums[c['name']] = sums.get(c['name'], 0) + c['score']
               counts[c['name']] = counts.get(c['name'], 0) + 1
       for name in sums:
           print('cat', name, round(sums[name] / counts[name], 2))
   "
   ```

2. If `rounds` is 0 (or the file is missing or empty), reply only:
   **"No practice rounds saved yet — run a mock round first."** and stop.

3. Otherwise, the weakest category is the one with the lowest average score
   (if tied, name all tied categories). Read the `feedback` lines for that
   category in `data/results.json` to ground the advice.

4. Reply in exactly this shape:

   ```
   Rounds practised: N
   Average total:    X/20
   Weakest category: <name> (avg Y/5)

   Focus next: <one concrete thing to do differently in the next round,
   aimed at the weakest category>
   ```

   Don't quote my saved answers back verbatim.
