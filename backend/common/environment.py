import os
from dotenv import load_dotenv

# Load environment variables only once
load_dotenv()

print("Environment variables loaded:", os.environ)


def get_env_var(key: str, default=None) -> str:
    """
    Return environment variable. Raises error if variable not set.
    If a default value is provided, return it instead of raising an error.
    """
    env_var = os.environ.get(key, default)
    if env_var is None:
        raise ValueError(f"Environment variable '{key}' is missing. "
                         f"Add '{key}' to .env file or set it in your environment.")
    return env_var


def get_nasa_api_key() -> str:
    """Fetch NASA API key."""
    return get_env_var('NASA_API_KEY')


def get_db_password() -> str:
    """Fetch database password."""
    return get_env_var('POSTGRES_PASSWORD')


def get_db_user() -> str:
    """Fetch database user."""
    return get_env_var('POSTGRES_USER')


def get_db_credentials() -> tuple[str, str]:
    """
    Fetch database credentials (user & password).
    Returns them as a tuple (username, password).
    """
    return get_db_user(), get_db_password()
