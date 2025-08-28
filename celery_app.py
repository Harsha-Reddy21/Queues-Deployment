import os
from kombu import Exchange, Queue
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

celery_app = Celery(
    "food_platform",
    broker=os.getenv("CELERY_BROKER_URL", REDIS_URL),
    backend=os.getenv("CELERY_RESULT_BACKEND", REDIS_URL),
    include=["tasks", "workflows", "enterprise_tasks"]  # import modules with tasks
)

# Exchanges & Queues
exchange = Exchange("tasks", type="direct")
celery_app.conf.task_default_exchange = "tasks"
celery_app.conf.task_default_exchange_type = "direct"

celery_app.conf.task_queues = (
    Queue("orders", exchange=exchange, routing_key="tasks.orders"),
    Queue("notifications", exchange=exchange, routing_key="tasks.notifications"),
    Queue("analytics", exchange=exchange, routing_key="tasks.analytics"),
    Queue("ml_processing", exchange=exchange, routing_key="tasks.ml_processing"),
    Queue("images", exchange=exchange, routing_key="tasks.images"),
    Queue("default", exchange=exchange, routing_key="tasks.default"),
)

# Routing: route tasks to specific queues
celery_app.conf.task_routes = {
    "process_order_workflow": {"queue": "orders", "routing_key": "tasks.orders"},
    "update_order_status": {"queue": "orders", "routing_key": "tasks.orders"},
    "send_realtime_notifications": {"queue": "notifications", "routing_key": "tasks.notifications"},
    "bulk_notification_campaign": {"queue": "notifications", "routing_key": "tasks.notifications"},
    "generate_business_analytics": {"queue": "analytics", "routing_key": "tasks.analytics"},
    "ml_recommendation_training": {"queue": "ml_processing", "routing_key": "tasks.ml_processing"},
    "process_menu_images": {"queue": "images", "routing_key": "tasks.images"},
}

# Worker and task tuning
celery_app.conf.update(
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_time_limit=60 * 10,      # 10 min hard
    task_soft_time_limit=60 * 9,  # 9 min soft
    result_expires=3600,
)
