from celery_app import celery_app
import time, random
from datetime import datetime

@celery_app.task(bind=True, name="generate_restaurant_report")
def generate_restaurant_report(self, cuisine_type: str):
    progress = [0, 25, 50, 75, 100]
    result = {
        "cuisine": cuisine_type,
        "total_restaurants": random.randint(50, 200),
        "average_rating": round(random.uniform(3.5, 4.8), 2),
        "popular_dishes": ["Dish A", "Dish B", "Dish C"],
        "generated_at": datetime.utcnow().isoformat()
    }
    for p in progress:
        self.update_state(state="PROGRESS", meta={"progress": p})
        time.sleep(1)
    return result

@celery_app.task(name="sync_restaurant_data")
def sync_restaurant_data(restaurant_id: int):
    time.sleep(3)
    return {"restaurant_id": restaurant_id, "status": "Synced", "timestamp": datetime.utcnow().isoformat()}

@celery_app.task(name="send_restaurant_notifications")
def send_restaurant_notifications(restaurant_data: dict, notification_type: str):
    time.sleep(2)
    return {"notified": True, "type": notification_type, "data": restaurant_data}

