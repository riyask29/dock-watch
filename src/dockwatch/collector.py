"""Dock Watch collector: fetch one snapshot of every Bluebikes station."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests

FEED_URL = "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json"
DATA_DIR = Path("data/raw/station_status")
BUCKET = os.environ.get("DOCKWATCH_BUCKET")


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


def snapshot_key(feed: dict) -> str:
    """S3 key with a Hive-style date folder, so Athena can skip other days."""
    feed_time = datetime.fromtimestamp(feed["last_updated"], tz=timezone.utc)
    return (f"station_status/dt={feed_time:%Y-%m-%d}/"
            f"station_status_{feed['last_updated']}.json")


def upload_snapshot(feed: dict, bucket: str) -> str:
    """Upload the raw feed to S3. Same feed twice = same key, so no duplicates."""
    key = snapshot_key(feed)
    boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=json.dumps(feed),
                                  ContentType="application/json")
    return f"s3://{bucket}/{key}"


def main() -> None:
    feed = fetch_status()
    stations = feed["data"]["stations"]
    where = upload_snapshot(feed, BUCKET) if BUCKET else save_snapshot(feed)
    print(f"saved {len(stations)} stations to {where}")


if __name__ == "__main__":
    main()