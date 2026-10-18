import csv, os, json, urllib.request
from collections import defaultdict

HOOK = os.environ["DISCORD_WEBHOOK"]

rows = list(csv.DictReader(open("data/snapshots.csv", encoding="utf-8")))
by = defaultdict(dict)
for r in rows:
    by[int(r["ts"])][r["governor_id"]] = r

times = sorted(by)
latest = times[-1]
prior = [t for t in times if t < latest]
if not prior:
    print("Not enough history yet")
    raise SystemExit

target = latest - 7 * 86400
base = min(prior, key=lambda t: abs(t - target))
cur, old = by[latest], by[base]

def p(r):
    return int(r["power"])

total_now = sum(p(r) for r in cur.values())
total_old = sum(p(r) for r in old.values())

both = [g for g in cur if g in old]
gains = sorted(((p(cur[g]) - p(old[g]), cur[g]["name"]) for g in both),
               reverse=True)
joined = [cur[g]["name"] for g in cur if g not in old]
left = [old[g]["name"] for g in old if g not in cur]
flat = [n for d, n in gains if d <= 0]

def short(names, limit=15):
    if not names:
        return "None"
    s = ", ".join(names[:limit])
    if len(names) > limit:
        s += f" (+{len(names) - limit} more)"
    return s

lines = [
    f"**MIS weekly report** (changes since <t:{base}:f>)",
    f"Members: **{len(cur)}** | Total power: **{total_now:,}** "
    f"({total_now - total_old:+,})",
    "",
    "**Top power gainers**",
]
for i, (d, n) in enumerate(gains[:10], 1):
    lines.append(f"{i}. {n}  {d:+,}")
lines += [
    "",
    f"**Joined:** {short(joined)}",
    f"**Left:** {short(left)}",
    f"**No power growth:** {short(flat)}",
]

payload = {"content": "\n".join(lines)[:1900],
           "allowed_mentions": {"parse": []}}
req = urllib.request.Request(
    HOOK, data=json.dumps(payload).encode(), method="POST",
    headers={"Content-Type": "application/json",
             "User-Agent": "mis-tracker"})
urllib.request.urlopen(req)
print("Posted")
