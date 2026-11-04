"""Dock Watch collector: fetch one snapshot of every Bluebikes station."""

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

FEED_URL = "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json"
DATA_DIR = Path("data/raw/station_status")


def fetch_status() -> dict:
    """Download the live feed. One request returns every station."""
    response = requests.get(FEED_URL, timeout=20)
    response.raise_for_status()
    return response.json()


def save_snapshot(feed: dict) -> Path:
    """Save the raw feed as one file, named by the feed's own timestamp."""
    feed_time = datetime.fromtimestamp(feed["last_updated"], tz=timezone.utc)
    folder = DATA_DIR / feed_time.strftime("%Y-%m-%d")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"station_status_{feed['last_updated']}.json"
    path.write_text(json.dumps(feed))
    return path


def main() -> None:
    feed = fetch_status()
    path = save_snapshot(feed)
    stations = feed["data"]["stations"]
    print(f"saved {len(stations)} stations to {path}")


if __name__ == "__main__":
    main()