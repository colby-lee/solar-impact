import os
import json
import time
from datetime import datetime, timedelta, timezone

import pika
from sqlalchemy import func
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import Counter, Histogram, CollectorRegistry, push_to_gateway

from data_collector.clients import NASAClient
from common import db, environment as env
from common.models.model import SolarFlare

# Initialize NASA client
client = NASAClient()

# Prometheus registry (for push mode)
registry = CollectorRegistry()

# Define Prometheus metrics (bind to custom registry)
COLLECTION_COUNTER = Counter(
    'solar_flare_collection_total',
    'Total number of solar flare collection events triggered',
    registry=registry
)
COLLECTION_DURATION = Histogram(
    'solar_flare_collection_duration_seconds',
    'Time in seconds spent collecting and inserting solar flare data',
    registry=registry
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
    """Periodically fetch and insert solar flare data from the NASA API."""
    print(f"Periodic data collection triggered at {datetime.now()}")
    sd, ed = compute_collection_range()
    start_time = time.time()

    COLLECTION_COUNTER.inc()
    client.fetch_and_insert_solar_flares(sd, ed)

    duration = time.time() - start_time
    COLLECTION_DURATION.observe(duration)
    push_metrics("periodic-collection")


def callback(ch, method, properties, body):
    """Handle incoming RabbitMQ messages for immediate data collection."""
    message = json.loads(body)
    start_date = message.get('start_date')
    end_date = message.get('end_date')
    print(f"Immediate data collection triggered for {start_date} to {end_date}")

    start_time = time.time()
    COLLECTION_COUNTER.inc()
    client.fetch_and_insert_solar_flares(start_date=start_date, end_date=end_date)

    duration = time.time() - start_time
    COLLECTION_DURATION.observe(duration)
    push_metrics("immediate-collection")


def start_listening():
    """Listen to RabbitMQ for incoming messages from FastAPI backend."""
    connection = pika.BlockingConnection(pika.URLParameters(env.get_rabbitmq_url()))
    channel = connection.channel()

    channel.queue_declare(queue='data_collection_queue', durable=True)
    channel.basic_consume(queue='data_collection_queue', on_message_callback=callback, auto_ack=True)

    print('Listening for messages to trigger data collection...')
    channel.start_consuming()


def push_metrics(job='solar-impact-collector'):
    """Push Prometheus metrics to Grafana Cloud."""
    url = os.getenv('GRAFANA_REMOTE_WRITE_URL')
    username = os.getenv('GRAFANA_USERNAME')
    password = os.getenv('GRAFANA_PASSWORD')

    if not url or not username or not password:
        print("Grafana Cloud config missing, skipping push")
        return

    try:
        push_to_gateway(
            url,
            job=job,
            registry=registry,
            auth=(username, password)
        )
        print("Metrics pushed to Grafana Cloud")
    except Exception as e:
        print(f'Error pushing metrics: {e}')


if __name__ == "__main__":
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            collect_data_periodically,
            'interval',
            hours=24,
            next_run_time=datetime.now()
        )
        scheduler.start()

        start_listening()

        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down gracefully...")
        scheduler.shutdown()
