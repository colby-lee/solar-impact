import pytest
import importlib
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from common.models.model import SolarFlare

# Create a TestClient fixture that instantiates the FastAPI app after the DatabaseManager override.
@pytest.fixture
def client(override_db):
    # Force a reload of the FastAPI app module so it uses the overridden DatabaseManager.
    import api.main as main_module
    importlib.reload(main_module)
    return TestClient(main_module.app)

@pytest.fixture
def create_test_flare():
    # Convert ISO strings to datetime objects with UTC offset.
    begin_time = datetime.fromisoformat("2099-12-31T23:59:59+00:00")
    peak_time = datetime.fromisoformat("2100-01-01T00:10:00+00:00")
    end_time = datetime.fromisoformat("2100-01-01T00:20:00+00:00")
    
    test_flare = SolarFlare(
        flr_id="2099-12-31T23:59:59-FLR-TEST",
        begin_time=begin_time,
        peak_time=peak_time,
        end_time=end_time,
        class_type="M9.9",
        source_location="N00E00",
        active_region_num=99999,
        linked_events=None
    )
    from common import db
    with db.DatabaseManager.session_scope() as session:
        session.add(test_flare)
        session.flush()  # Ensure the record is flushed to the DB.
        session.commit()
        flare = session.query(SolarFlare).filter_by(flr_id="2099-12-31T23:59:59-FLR-TEST").first()
        print("---------------------------------------------------------------------------------")
        print("Inserted test flare:", flare)
        print("---------------------------------------------------------------------------------")
    return test_flare

def test_get_solar_flares_empty(client):
    response = client.get("/api/solar-flares", params={
        "start_date": "2100-01-01T00:00:00",
        "end_date": "2100-01-02T00:00:00"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_solar_flare_not_found(client):
    response = client.get("/api/solar-flares/NonExistentID")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_get_solar_flare_found(client, create_test_flare):
    response = client.get(f"/api/solar-flares/{create_test_flare.flr_id}")
    # Expect 200 if the record is found.
    assert response.status_code == 200, f"Response: {response.json()}"
    data = response.json()
    assert data.get("flr_id") == create_test_flare.flr_id
    assert data.get("class_type") == "M9.9"

def _dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

@pytest.fixture
def seed_three():
    from common import db
    with db.DatabaseManager.session_scope() as s:
        s.query(SolarFlare).delete()
        a = SolarFlare(
            flr_id="A",
            begin_time=_dt("2024-06-10T00:00:00Z"),
            peak_time=_dt("2024-06-10T00:05:00Z"),
            end_time=_dt("2024-06-10T00:10:00Z"),
            class_type="C1.0",
            source_location="N00E00",
            active_region_num=1,
            linked_events=None,
        )
        b = SolarFlare(
            flr_id="B",
            begin_time=_dt("2024-06-20T00:00:00Z"),
            peak_time=_dt("2024-06-20T00:05:00Z"),
            end_time=_dt("2024-06-20T00:10:00Z"),
            class_type="M1.0",
            source_location="N00E00",
            active_region_num=2,
            linked_events=None,
        )
        c = SolarFlare(
            flr_id="C",
            begin_time=_dt("2024-07-01T00:00:00Z"),
            peak_time=_dt("2024-07-01T00:05:00Z"),
            end_time=_dt("2024-07-01T00:10:00Z"),
            class_type="X1.0",
            source_location="N00E00",
            active_region_num=3,
            linked_events=None,
        )
        s.add_all([a, b, c])

def test_filter_range(client, seed_three):
    r = client.get("/api/solar-flares", params={
        "start_date": "2024-06-15T00:00:00Z",
        "end_date": "2024-06-30T23:59:59Z",
    })
    assert r.status_code == 200
    ids = [x["flr_id"] for x in r.json()]
    assert ids == ["B"]

def test_get_by_id_found_and_missing(client):
    from common import db
    with db.DatabaseManager.session_scope() as s:
        s.query(SolarFlare).delete()
        x = SolarFlare(
            flr_id="ID-OK",
            begin_time=datetime.now(timezone.utc),
            peak_time=datetime.now(timezone.utc) + timedelta(minutes=5),
            end_time=datetime.now(timezone.utc) + timedelta(minutes=10),
            class_type="M1.2",
            source_location="N10E10",
            active_region_num=123,
            linked_events=None,
        )
        s.add(x)
    r1 = client.get("/api/solar-flares/ID-OK")
    r2 = client.get("/api/solar-flares/ID-MISSING")
    assert r1.status_code == 200
    assert r1.json()["flr_id"] == "ID-OK"
    assert r2.status_code == 404
