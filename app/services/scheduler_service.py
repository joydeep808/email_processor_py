import datetime
import json
import redis
import pika
from app.services.redis_service import RedisService
from app.api.deps import get_rabbitmq_service, get_redis_service


def check_records_and_publish():
       connection = get_rabbitmq_service()
       pending_emails = get_redis_service().get_pending_emails()
       for email in pending_emails:
           email['created_at'] = int(email['created_at'].timestamp())
           connection.publish_message(json.dumps(email))

