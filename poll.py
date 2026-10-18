import csv, os, time, requests

KEY = os.environ["MIGHTPULSE_KEY"]
KID, TAG = 277, "MIS"
FILE = "data/snapshots.csv"

r = requests.get(
    f"https://api.mightpulse.com/v1/alliances/{KID}/{TAG}",
    params={"include": "info,roster"},
    headers={"Authorization": f"Bearer {KEY}"},
    timeout=120,
)
r.raise_for_status()
members = r.json()["members"]

os.makedirs("data", exist_ok=True)
is_new = not os.path.exists(FILE)
now = int(time.time())

with open(FILE, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if is_new:
        w.writerow(["ts", "governor_id", "name", "power",
                    "kills", "tc_level", "rank"])
    for m in members:
        w.writerow([now, m["governor_id"], m["nick_name"], m["power"],
                    m["kills"], m["town_center_level"],
                    m["alliance_rank_label"]])

print(f"Saved {len(members)} members")
