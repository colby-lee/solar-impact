import re
import requests
from datetime import datetime
from typing import Any, Dict, List, Union

# Importing environment variables, database utilities, and models
from common import environment as env
from common import db
from common.utils import parse_time
from common.models.model import SolarFlare


class Client:
    """
    Base class for API clients.
    Provides a generic method for making GET requests.
    """
    def get_data(self, url: str, params: Dict[str, Any] = None) -> Union[Dict[str, Any], List[Any]]:
        """
        Fetch data from the given URL with optional query parameters.
        Handles common HTTP errors gracefully.
        """
        try:
            response = requests.get(url, params=params)  # Pass parameters for dynamic queries
            response.raise_for_status()  # Raise HTTP errors if any
            return response.json()  # Return the JSON response
        except requests.exceptions.Timeout:
            print("Error: Request timed out.")
        except requests.exceptions.ConnectionError:
            print("Error: Connection issue.")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error {http_err}")
        except ValueError as json_err:
            print(f"Error decoding JSON: {json_err}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        return []  # Return an empty list on error


class NASAClient(Client):
    """
    Client to interact with NASA's Solar Flare API.
    Handles fetching, processing, and inserting solar flare data into the database.
    """
    def __init__(self):
        # Fetch the API key from environment variables
        self.API_KEY = env.get_nasa_api_key()
        # Base URL for the API
        self.url = f'https://api.nasa.gov/DONKI/FLR'
        super().__init__()  # Initialize the parent class

    def fetch_flare_data(self, start_date=None, end_date=None) -> Union[Dict[str, Any], List[Any]]:
        """
        Fetch solar flare data from NASA API.
        Allows filtering by optional start and end dates.
        """
        # Construct query parameters dynamically
        params = {"api_key": self.API_KEY}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        # Fetch data using the inherited method
        try:
            return self.get_data(self.url, params=params)
        except Exception as e:
            print(f"Error fetching solar flare data: {e}")
            return []

    @staticmethod
    def extract_flr_id(payload_flr_id: str) -> Union[str, None]:
        """
        Extracts the FLR-001-like identifier from a given flrID string using regex.
        :param payload_flr_id: Raw flrID from the API payload.
        :return: Extracted FLR identifier or None if not matched.
        """
        match = re.search(r'([A-Z]+-\d+)', payload_flr_id)
        if match:
            return match.group(1)  # Return the matched identifier
        print(f"Regex did not match for payload: {payload_flr_id}")
        return None

    @staticmethod
    def map_nasa_payload_to_solar_flare(payload: Dict[str, Any]) -> Union[SolarFlare, None]:
        """
        Maps a single payload from NASA's API response to a SolarFlare model instance.
        Handles data transformation and error handling.
        :param payload: The raw JSON response for a single solar flare event.
        :return: A `SolarFlare` model instance, or None if mapping fails.
        """
        try:
            # Extract and transform fields from the payload
            flr_id_raw = payload.get("flrID", "")
            flr_id = NASAClient.extract_flr_id(flr_id_raw)  # Extract unique identifier
            return SolarFlare(
                flr_id=flr_id,
                begin_time=parse_time(payload["beginTime"]),
                peak_time=parse_time(payload["peakTime"]),
                end_time=parse_time(payload["endTime"]) if payload.get("endTime") else None,
                class_type=payload.get("classType", ""),
                source_location=payload.get("sourceLocation", ""),
                active_region_num=payload.get("activeRegionNum"),
                linked_events=payload.get("linkedEvents"),  # Retain JSON structure
            )
        except KeyError as e:
            print(f"Missing expected field in payload: {e}")
        except ValueError as e:
            print(f"Invalid data format in payload: {e}")
        except Exception as e:
            print(f"Unexpected error while mapping payload: {e}")
        return None

    @staticmethod
    def process_solar_flares(solar_flare_data: List[Dict[str, Any]]) -> List[SolarFlare]:
        """
        Converts raw solar flare data into a list of SolarFlare instances.
        Skips invalid or malformed data.
        :param solar_flare_data: List of raw solar flare data from the API.
        :return: List of valid SolarFlare instances.
        """
        processed_flares = []
        for payload in solar_flare_data:
            solar_flare = NASAClient.map_nasa_payload_to_solar_flare(payload)
            if solar_flare:  # Skip invalid payloads
                processed_flares.append(solar_flare)
        return processed_flares

    def fetch_and_insert_solar_flares(self):
        """
        Fetch solar flare data from NASA API and insert them into the database.
        Ensures no duplicate entries are added.
        """
        # Fetch raw data from the API
        solar_flare_data = self.fetch_flare_data()
        if not isinstance(solar_flare_data, list):  # Validate response format
            print("Invalid API response format.")
            return

        # Process raw data into SolarFlare instances
        solar_flares = self.process_solar_flares(solar_flare_data)
        with db.DatabaseManager.session_scope() as session:
            for solar_flare in solar_flares:
                # Check for duplicates before inserting
                if not session.query(SolarFlare).filter_by(flr_id=solar_flare.flr_id).first():
                    session.add(solar_flare)  # Add only unique entries
