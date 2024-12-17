import sys
import os
import re
import requests 
from datetime import datetime
from typing import Any, Dict, List, Union

from common import environment as env
from common import db
from common.utils import parse_time
from models.model import SolarFlare




class Client:
    '''
    Base class for API clients.
    '''
    def __init__(self):
        ...
        
    def get_data(self, url: str) -> Union[Dict[str, Any], List[Any]]:
        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.Timeout:
            print('Error: Request timed out.')
        except requests.exceptions.ConnectionError:
            print('Error: Connection issue.')
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error {http_err}')
        except ValueError as json_err:
            print(f'Error decoding JSON: {json_err}')
        except Exception as e:
            print(f'Unexpected error: {e}')
        

class NASAClient(Client):
    def __init__(self):
        self.API_KEY = env.get_nasa_api_key()
        # TODO:
        # Change url to acccept date range
        # Query data store for most recent data
        # If requested date occurs outside range of data store, request data with date range
        # url = f"https://api.nasa.gov/DONKI/FLR?startDate={start_date}&endDate={end_date}&api_key={API_KEY}"
        self.url = f'https://api.nasa.gov/DONKI/FLR?api_key={self.API_KEY}'
        super().__init__()

    def fetch_flare_data(self) -> Union[Dict[str, Any], List[Any]]:
        return self.get_data(self.url)
    
    @staticmethod
    def extract_flr_id(payload_flr_id):
            """
            Extracts the FLR-001-like identifier from a given flrID string using regex.
            """
            match = re.search(r'([A-Z]+-\d+)', payload_flr_id)
            if match:
                return match.group(1)  # Return the first match
            else:
                print(f"Regex did not match for payload: {payload_flr_id}")
                return None

    
    @staticmethod
    def map_nasa_payload_to_solar_flare(payload):
        """
        Maps the payload from NASA's API response to a SolarFlare model instance.
        Ensures that all necessary transformations are performed.
        
        :param payload: The raw JSON response for a single solar flare event.
        :return: A `SolarFlare` model instance, or None if mapping fails.
        """
        try:
            # Transform and map the payload to a SolarFlare instance
            flr_id_raw = payload.get("flrID", "")
            # Extract only the unique identifier (e.g., 'FLR-001') from the flrID payload
            flr_id = NASAClient.extract_flr_id(flr_id_raw)

            return SolarFlare(
                flr_id=flr_id,
                begin_time=parse_time(payload["beginTime"]),
                peak_time=parse_time(payload["peakTime"]),
                end_time=parse_time(payload["endTime"]) if payload.get("endTime") else None,
                class_type=payload.get("classType", ""),
                source_location=payload.get("sourceLocation", ""),
                active_region_num=payload.get("activeRegionNum"),
                linked_events=payload.get("linkedEvents"),  # Keep JSON structure if available
            )
        except KeyError as e:
            print(f"Missing expected field in payload: {e}")
        except ValueError as e:
            print(f"Invalid data format in payload: {e}")
        except Exception as e:
            print(f"Unexpected error while mapping payload: {e}")
        return None
    
    def fetch_and_insert_solar_flares(self):
        """
        Fetch solar flares from NASA API and insert them into the database.
        :param start_date: Start date for fetching data (YYYY-MM-DD)
        :param end_date: End date for fetching data (YYYY-MM-DD)
        """
        solar_flare_data = self.fetch_flare_data()
        
        with db.DatabaseManager.session_scope() as session:
            for payload in solar_flare_data:
                solar_flare = self.map_nasa_payload_to_solar_flare(payload)
                if solar_flare and not session.query(SolarFlare).filter_by(flr_id=solar_flare.flr_id).first():
                    session.add(solar_flare)


