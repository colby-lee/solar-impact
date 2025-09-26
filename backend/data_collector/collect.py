import json
import time
from datetime import datetime, timedelta, timezone
import threading

import pika
from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import start_http_server, Counter, Histogram

from data_collector.clients import NASAClient
from common import db, environment as env
from common.models.model import SolarFlare

# Initialize NASA client
client = NASAClient()

# Define Prometheus metrics
COLLECTION_COUNTER = Counter(
    'solar_flare_collection_total',
    'Total number of solar flare collection events triggered'
)
COLLECTION_DURATION = Histogram(
    'solar_flare_collection_duration_seconds',
    'Time in seconds spent collecting and inserting solar flare data'
)

def compute_collection_range():
    """Collect since last stored flare; if empty DB, collect the last 7 days."""
    with db.DatabaseManager.session_scope() as session:
        last = session.query(func.max(SolarFlare.begin_time)).scalar()

    now_utc = datetime.now(timezone.utc)
    if last:
        start = (last + timedelta(seconds=1)).date().isoformat()   
    else:
        start = (now_utc - timedelta(days=7)).date().isoformat()   
    end = now_utc.date().isoformat()
    return start, end

def collect_data_periodically():
    """
    Periodically fetch and insert solar flare data from the NASA API.
    """
    print(f"Periodic data collection triggered at {datetime.now()}")
    sd, ed = compute_collection_range()
    start_time = time.time()
    COLLECTION_COUNTER.inc()  # Increment counter for periodic collection
    client.fetch_and_insert_solar_flares(sd, ed)
    duration = time.time() - start_time
    COLLECTION_DURATION.observe(duration)
    
def callback(ch, method, properties, body):
    """
    Callback function to handle incoming messages from RabbitMQ.
    It will trigger data collection when a new message is received.
    """
    message = json.loads(body)
    start_date = message.get('start_date')
    end_date = message.get('end_date')
    print(f"Immediate data collection triggered for {start_date} to {end_date}")
    start_time = time.time()
    COLLECTION_COUNTER.inc()  # Increment counter for immediate trigger
    client.fetch_and_insert_solar_flares(start_date=start_date, end_date=end_date)
    duration = time.time() - start_time
    COLLECTION_DURATION.observe(duration)

def start_listening():
    """
    Start listening to the RabbitMQ queue for incoming messages.
    This listens for trigger messages from the FastAPI backend.
    """
    connection = pika.BlockingConnection(pika.URLParameters(host=env.get_rabbitmq_url()))
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue='data_collection_queue', durable=True)

    # Set up a consumer to process messages from the queue
    channel.basic_consume(queue='data_collection_queue', on_message_callback=callback, auto_ack=True)

    print('Listening for messages to trigger data collection...')
    channel.start_consuming()

def start_prometheus_server():
    """
    Start the Prometheus metrics HTTP server on port 8001.
    """
    start_http_server(8001)
    print("Prometheus metrics server started on port 8001")

if __name__ == "__main__":
    try:
        # Start Prometheus metrics server in a background thread
        # This may need to be removed in production
        threading.Thread(target=start_prometheus_server, daemon=True).start()

        # Configure the periodic task to collect data every 24 hours
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            collect_data_periodically,
              'interval',
                hours=24, 
                next_run_time=datetime.now()
                )
        scheduler.start()

        # Start listening to RabbitMQ for trigger messages (blocking call)
        start_listening()

        # If start_listening ever returns, keep the process alive
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down gracefully...")
        scheduler.shutdown()
