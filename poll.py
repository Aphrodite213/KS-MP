import csv, os, time, requests

KEY = os.environ["MIGHTPULSE_KEY"]
KID, TAG = 277, "MIS"
FILE = "data/snapshots.csv"
EVENTS = "data/events.csv"

r = requests.get(
    f"https://api.mightpulse.com/v1/alliances/{KID}/{TAG}",
    params={"include": "info,roster"},
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=120,
)
r.raise_for_status()
members = r.json()["members"]

os.makedirs("data", exist_ok=True)
now = int(time.time())

# Roster from the previous snapshot
prev = {}
if os.path.exists(FILE):
    with open(FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if rows:
        last = max(int(x["ts"]) for x in rows)
        prev = {x["governor_id"]: x["name"]
                for x in rows if int(x["ts"]) == last}

cur = {str(m["governor_id"]): m["nick_name"] for m in members}

# Compare (skipped if the roster looks incomplete, to avoid false "left" rows)
events = []
if prev and len(cur) >= len(prev) * 0.5:
    for g, n in cur.items():
        if g not in prev:
            events.append([now, "joined", g, n, ""])
        elif prev[g] != n:
            events.append([now, "renamed", g, n, prev[g]])
    for g, n in prev.items():
        if g not in cur:
            events.append([now, "left", g, n, ""])

if events:
    new_file = not os.path.exists(EVENTS)
    with open(EVENTS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["ts", "type", "governor_id", "name", "old_name"])
        w.writerows(events)

# Save the snapshot as before
is_new = not os.path.exists(FILE)
with open(FILE, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if is_new:
        w.writerow(["ts", "governor_id", "name", "power",
                    "kills", "tc_level", "rank"])
    for m in members:
        w.writerow([now, m["governor_id"], m["nick_name"], m["power"],
                    m["kills"], m["town_center_level"],
                    m["alliance_rank_label"]])

print(f"Saved {len(members)} members, {len(events)} changes")
