from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------

ROOMS = [
    "Room.U23",
    "Room.U21",
    "Room.U81",
]

BASE_URL = "https://detskeridag.sdu.dk/room/api/events/te/"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

session = requests.Session()
session.headers.update(HEADERS)

# -------------------------
# ROOM CHECK LOGIC
# -------------------------

def check_room(room_id):
    url = f"{BASE_URL}{room_id}/"
    response = session.get(url, timeout=10)

    if response.status_code != 200:
        return f"ERROR {response.status_code}"

    data = response.json()

    if not data:
        return "FREE ALL DAY"

    now_time = datetime.now().time()

    for event in data:
        start_time = datetime.fromisoformat(event["StartTime"]).time()
        end_time = datetime.fromisoformat(event["EndTime"]).time()

        if start_time <= now_time < end_time:
            return f"BUSY NOW ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})"

    return "FREE NOW"


def check_all_rooms():
    results = []

    for room in ROOMS:
        try:
            status = check_room(room)
        except Exception as e:
            status = f"ERROR: {e}"

        results.append({
            "room": room,
            "status": status
        })

    return results

# -------------------------
# PRIMARY ROUTE
# -------------------------

@app.route("/")
def home():
    results = check_all_rooms()
    current_time = datetime.now().strftime("%H:%M")
    free_count = sum(1 for r in results if "FREE" in r["status"])

    return render_template(
        "rooms.html",
        results=results,
        current_time=current_time,
        free_count=free_count
    )

# -------------------------
# LOCAL RUN
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)