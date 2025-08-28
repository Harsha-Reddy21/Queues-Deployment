import os 
from celery import Celery
from kombu import Queue, Exchange

REDIS_URL=os.getenv("REDIS_URL","redis://localhost:6379/0")

celery_app=Celery(
    'queues_deployment',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks','workflows'],
)


default_exchange=Exchange('tasks',type='direct')

celery_app.conf.task_default_exchange='tasks'
celery_app.conf.task_default_exchange_type='direct'
celery_app.conf.task_default_routing_key='tasks.low'



celery_app.conf.task_queues=(
    Queue('q.high',exchange=default_exchange,routing_key='tasks.high'),
    Queue('q.medium',exchange=default_exchange,routing_key='tasks.medium'),
    Queue('q.low',exchange=default_exchange,routing_key='tasks.low'),
    Queue('q.images',exchange=default_exchange,routing_key='tasks.images'),
    Queue('q.analytics',exchange=default_exchange,routing_key='tasks.analytics')
)

celery_app.conf.task_routes = {
    "analyze_menu_performance": {"queue": "q.analytics", "routing_key": "tasks.analytics"},
    "bulk_menu_update":         {"queue": "q.medium",    "routing_key": "tasks.medium"},
    "process_menu_images":      {"queue": "q.images",    "routing_key": "tasks.images"},

    # Example routes for workflow steps (below)
    "create_restaurant_task":   {"queue": "q.high",      "routing_key": "tasks.high"},
    "sync_with_maps_api":       {"queue": "q.medium",    "routing_key": "tasks.medium"},
    "generate_qr_code":         {"queue": "q.medium",    "routing_key": "tasks.medium"},
    "send_welcome_notification":{"queue": "q.low",       "routing_key": "tasks.low"},
    "process_menu_item":        {"queue": "q.medium",    "routing_key": "tasks.medium"},
    "generate_menu_summary":    {"queue": "q.analytics", "routing_key": "tasks.analytics"},
}


celery_app.conf.update(
    task_track_started=True,
    task_time_limit=60 * 10,  # 10 minutes hard limit
    task_soft_time_limit=60 * 9,
    worker_send_task_events=True,
    task_send_sent_event=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,   # fair scheduling
    task_acks_late=True,            # acknowledge after finish
    broker_pool_limit=10,
)