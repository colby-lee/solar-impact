from datetime import datetime


def parse_time(time_str: str) -> datetime:
    """
    Parse ISO 8601 timestamps robustly, with or without seconds, and handle trailing 'Z'.
    """
    if time_str.endswith('Z'):
        time_str = time_str[:-1]  # Remove trailing 'Z' for UTC

    # Handle missing seconds by appending ":00" only if necessary
    if len(time_str) == 16:  # If string is like 'YYYY-MM-DDTHH:MM'
        time_str += ":00"
    
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
