import os
from dotenv import load_dotenv

# Load environment variables only once if deployed locally, 
# otherwise heroku is set through other means
if os.environ.get("DYNO") is None:  
    load_dotenv()


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


def get_database_url() -> str:
    """
    Prefer DATABASE_URL (Heroku). 
    Fall back to local POSTGRES_USER + POSTGRES_PASSWORD if not set.
    """
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # Heroku DATABASE_URL can be postgres:// instead of postgresql://
        return db_url.replace("postgres://", "postgresql://", 1)

    # Local fallback
    user = get_db_user()
    password = get_db_password()
    host = get_db_host()
    port = get_db_port()
    dbname = get_db_name()

    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def get_db_host() -> str:
    return get_env_var('POSTGRES_HOST', 'localhost')


def get_db_port() -> int:
    return int(get_env_var('POSTGRES_PORT', 5432))


def get_db_name() -> str:
    return get_env_var('POSTGRES_DB', 'solarflare')


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


def get_rabbitmq_url() -> str:
    '''Get RabbitMQ url, try for 
    CLOUDAMQP_URL (Heroku) first then local'''
    mqurl = os.environ.get("CLOUDAMQP_URL")
    if mqurl:
        return mqurl
    return os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
