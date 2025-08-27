
import os 
from celery import Celery

REDIS_URL=os.getenv("REDIS_URL","redis://localhost:6379/0")


celery_app=Celery(
    'zomato_v1',
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.task_track_started=True 
celery_app.conf.result_expires=3600
celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True
)