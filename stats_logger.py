import os
from datetime import datetime, timedelta
from collections import defaultdict

STATS_DIR = "data"
STATS_FILE = os.path.join(STATS_DIR, "stats.log")

os.makedirs(STATS_DIR, exist_ok=True)

# memory cache (last 5 min users)
ACTIVE_USERS = {}  # user_id -> last_active_time


def _now():
    return datetime.now()


def _format_time(dt: datetime):
    # NO SECONDS (as you asked)
    return dt.strftime("%Y-%m-%d | %H:%M")


def log_search(user_id: int, user_name: str, keyword: str):
    now = _now()
    ACTIVE_USERS[user_id] = now

    # remove users inactive for >5 minutes
    cutoff = now - timedelta(minutes=5)
    for uid in list(ACTIVE_USERS.keys()):
        if ACTIVE_USERS[uid] < cutoff:
            del ACTIVE_USERS[uid]

    active_count = len(ACTIVE_USERS)

    line = (
        f"{_format_time(now)} | "
        f"{active_count} | "
        f"{user_name} | "
        f"{user_id} | "
        f"{keyword}\n"
    )

    with open(STATS_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def log_snapshot():
    now = _now()

    cutoff = now - timedelta(minutes=5)
    for uid in list(ACTIVE_USERS.keys()):
        if ACTIVE_USERS[uid] < cutoff:
            del ACTIVE_USERS[uid]

    active_count = len(ACTIVE_USERS)

    line = (
        f"{_format_time(now)} | "
        f"{active_count} | "
        f"- | - | SNAPSHOT\n"
    )

    with open(STATS_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def get_stats(hours: int = 24):
    cutoff = _now() - timedelta(hours=hours)
    users = set()
    keywords = defaultdict(int)

    if not os.path.exists(STATS_FILE):
        return 0, {}

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                parts = [p.strip() for p in line.split("|")]
                dt = datetime.strptime(parts[0] + " | " + parts[1], "%Y-%m-%d | %H:%M")
                if dt < cutoff:
                    continue

                user_id = parts[4]
                keyword = parts[5]

                if user_id != "-" and keyword != "SNAPSHOT":
                    users.add(user_id)
                    keywords[keyword] += 1
            except Exception:
                continue

    return len(users), dict(keywords)