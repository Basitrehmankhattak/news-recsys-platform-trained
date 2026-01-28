import requests
import random
import time

BASE_URL = "http://localhost:8000"

USERS = [
    {"anonymous_id": "anon_real_001"},
    {"anonymous_id": "anon_rankgen_002"},
    {"anonymous_id": "anon_rankgen_003"},
]

# -------------------------
# Start sessions
# -------------------------
sessions = {}

for user in USERS:
    r = requests.post(
        f"{BASE_URL}/session/start",
        json={
            "anonymous_id": user["anonymous_id"],
            "device_type": "web",
            "app_version": "0.1",
            "user_agent": "auto",
            "referrer": "auto"
        }
    )
    r.raise_for_status()
    sessions[user["anonymous_id"]] = r.json()["session_id"]

print("Sessions:", sessions)

# -------------------------
# CONFIG
# -------------------------
TOTAL_IMPRESSIONS = 50
SLEEP_SECONDS = 0.3  # keep DB happy

# click behavior probabilities
PROB_NO_CLICK = 0.2
PROB_ONE_CLICK = 0.6
PROB_TWO_CLICK = 0.2

# -------------------------
# Main loop
# -------------------------
for i in range(TOTAL_IMPRESSIONS):
    user = random.choice(USERS)
    anon_id = user["anonymous_id"]
    session_id = sessions[anon_id]

    # 1. Get recommendations
    r = requests.post(
        f"{BASE_URL}/recommendations",
        json={
            "session_id": session_id,
            "user_id": None,
            "anonymous_id": anon_id,
            "surface": "home",
            "page_size": 10,
            "locale": "en-US"
        }
    )
    r.raise_for_status()
    data = r.json()

    impression_id = data["impression_id"]
    items = data["items"]

    print(f"\n[{i+1}/{TOTAL_IMPRESSIONS}] impression {impression_id} user={anon_id}")

    # 2. Decide click pattern
    p = random.random()

    if p < PROB_NO_CLICK:
        print("  -> NO CLICK")

    elif p < PROB_NO_CLICK + PROB_ONE_CLICK:
        item = random.choice(items)
        print(f"  -> CLICK 1: {item['item_id']} pos={item['position']}")
        requests.post(
            f"{BASE_URL}/click",
            json={
                "impression_id": impression_id,
                "item_id": item["item_id"],
                "position": item["position"]
            }
        )

    else:
        clicks = random.sample(items, 2)
        for item in clicks:
            print(f"  -> CLICK 2: {item['item_id']} pos={item['position']}")
            requests.post(
                f"{BASE_URL}/click",
                json={
                    "impression_id": impression_id,
                    "item_id": item["item_id"],
                    "position": item["position"]
                }
            )

    time.sleep(SLEEP_SECONDS)

print("\nDONE — interaction generation complete")
