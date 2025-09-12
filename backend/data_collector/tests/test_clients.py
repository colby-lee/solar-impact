import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from sqlalchemy import select
from common.models.model import SolarFlare
from common import db as dbmod
from common.utils import parse_time

from data_collector.clients import NASAClient, Client, _to_ymd


def test__to_ymd_and_parse_time():
    assert _to_ymd("2024-01-02T03:04:05Z") == "2024-01-02"
    assert _to_ymd("2024-01-02T03:04:05+00:00") == "2024-01-02"
    assert _to_ymd("2024-01-02") == "2024-01-02"
    assert _to_ymd(None) is None
    dt = parse_time("2024-01-02T03:04Z")
    assert isinstance(dt, datetime)


def test_map_payload_variants():
    payload1 = {
        "flrID": "2025-01-21T10:08:00-FLR-001",
        "beginTime": "2025-01-21T10:00Z",
        "peakTime": "2025-01-21T10:08Z",
        "endTime": None,
        "classType": "M1.0",
        "sourceLocation": "N10E10",
        "activeRegionNum": 12345,
        "linkedEvents": None,
    }
    m1 = NASAClient.map_nasa_payload_to_solar_flare(payload1)
    assert isinstance(m1, SolarFlare)
    assert m1.flr_id == "2025-01-21T10:08:00-FLR-001"

    payload2 = {
        "flrID": "weird",
        "beginTime": "2025-01-21T10:00Z",
        "peakTime": "2025-01-21T10:08Z",
        "endTime": "2025-01-21T10:20Z",
    }
    m2 = NASAClient.map_nasa_payload_to_solar_flare(payload2)
    assert m2 is not None
    assert m2.flr_id == "weird"


def test_client_get_data_http_error(monkeypatch):
    c = Client()
    class R:
        def raise_for_status(self): 
            from requests import HTTPError
            raise HTTPError("boom")
    monkeypatch.setattr("requests.get", lambda *a, **k: R())
    out = c.get_data("http://x")
    assert out == []
