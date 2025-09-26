from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api.main import app  
from common.models.model import SolarFlare  

client = TestClient(app)

# Mock SolarFlare data
mock_flare_1 = MagicMock(spec=SolarFlare)
mock_flare_1.to_dict.return_value = {
    "flr_id": "FLR-001",
    "begin_time": "2024-11-17T10:38:00",
    "peak_time": "2024-11-17T12:00:00",
    "end_time": "2024-11-17T14:00:00",
    "class_type": "X1.0",
    "source_location": "AR12345",
    "active_region_num": 12345,
    "linked_events": {},
}

mock_flare_2 = MagicMock(spec=SolarFlare)
mock_flare_2.to_dict.return_value = {
    "flr_id": "FLR-002",
    "begin_time": "2024-11-18T10:38:00",
    "peak_time": "2024-11-18T12:00:00",
    "end_time": "2024-11-18T14:00:00",
    "class_type": "M2.0",
    "source_location": "AR54321",
    "active_region_num": 54321,
    "linked_events": {},
}


def test_get_all_solar_flares():
    # Patch just the query method of the session to return mock data
    with patch("api.endpoints.solar_flare.DatabaseManager.session_scope") as mock_session_scope:
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_flare_1, mock_flare_2]
        mock_session.query.return_value = mock_query
        mock_session_scope.return_value.__enter__.return_value = mock_session
        
        response = client.get("/api/solar-flares")

    # Debugging output
    print("Mock session query calls:", mock_session.query.mock_calls)
    print("Response JSON:", response.json())

    # Check the response
    assert response.status_code == 200
    assert response.json() == [
        mock_flare_1.to_dict.return_value,
        mock_flare_2.to_dict.return_value,
    ]



def test_get_solar_flare_found():
    # Patch just the query method of the session to return mock data
    with patch("api.endpoints.solar_flare.DatabaseManager.session_scope") as mock_session_scope:
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_flare_1
        mock_session.query.return_value = mock_query
        mock_session_scope.return_value.__enter__.return_value = mock_session
        
        response = client.get("/api/solar-flares/FLR-001")
    
    assert response.status_code == 200
    assert response.json() == mock_flare_1.to_dict.return_value


def test_get_solar_flare_not_found():
    # Patch just the query method of the session to simulate not finding the flare
    with patch("api.endpoints.solar_flare.DatabaseManager.session_scope") as mock_session_scope:
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None  # Simulate no match found
        mock_session.query.return_value = mock_query
        mock_session_scope.return_value.__enter__.return_value = mock_session
        
        response = client.get("/api/solar-flares/FLR-999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Solar flare not found"