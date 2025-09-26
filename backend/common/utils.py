import json
from datetime import datetime

import pika

import common.environment as env


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


def send_rabbitmq_message(queue_name: str, message: dict):
    """
    Sends a message to a RabbitMQ queue.
    """
    try:
        # Establish connection to RabbitMQ server
        connection = pika.BlockingConnection(pika.URLParameters(env.get_rabbitmq_url())) 
        channel = connection.channel()

        # Ensure the queue exists
        channel.queue_declare(queue=queue_name, durable=True)

        # Send the message (convert dict to JSON)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make the message persistent
            )
        )

        print(f" [x] Sent {message}")
        connection.close()

    except Exception as e:
        print(f"Error sending message to RabbitMQ: {e}")