"""Tests for the collector. No internet needed: we use a tiny fake feed."""
from dockwatch import collector


def fake_feed(last_updated: int) -> dict:
    return {"last_updated": last_updated, "ttl": 60,
            "data": {"stations": [{"station_id": "a", "num_bikes_available": 3}]}}


def test_file_is_named_by_feed_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(collector, "DATA_DIR", tmp_path)
    path = collector.save_snapshot(fake_feed(1793830944))
    assert path.name == "station_status_1793830944.json"
    assert path.parent.name == "2026-11-04"


def test_same_feed_twice_makes_one_file(tmp_path, monkeypatch):
    monkeypatch.setattr(collector, "DATA_DIR", tmp_path)
    collector.save_snapshot(fake_feed(1793830944))
    collector.save_snapshot(fake_feed(1793830944))
    assert len(list(tmp_path.rglob("*.json"))) == 1