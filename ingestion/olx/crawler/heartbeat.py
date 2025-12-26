import time
from config import HEARTBEAT_FILE


def update_heartbeat():
    with open(HEARTBEAT_FILE, "w") as f:
        f.write(str(time.time()))
