from celery import chain, group, chord
from celery_app import celery_app
from datetime import datetime
import time

# ----- Example workflow building blocks -----
@celery_app.task(name="create_restaurant_task")
def create_restaurant_task(restaurant_data: dict):
    # Pretend DB insert
    time.sleep(0.5)
    return {**restaurant_data, "created_at": datetime.utcnow().isoformat()}

@celery_app.task(name="sync_with_maps_api", autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def sync_with_maps_api(prev_result: dict):
    time.sleep(0.8)
    prev_result["maps_synced"] = True
    return prev_result

@celery_app.task(name="generate_qr_code")
def generate_qr_code(prev_result: dict):
    time.sleep(0.3)
    prev_result["qr_code_url"] = f"https://cdn.qr/restaurant/{prev_result.get('id','new')}.png"
    return prev_result

@celery_app.task(name="send_welcome_notification")
def send_welcome_notification(prev_result: dict):
    time.sleep(0.2)
    prev_result["welcome_notified"] = True
    return prev_result

@celery_app.task(name="process_menu_item")
def process_menu_item(restaurant_id: int, item: dict):
    time.sleep(0.2)
    return {"restaurant_id": restaurant_id, "item_id": item["id"], "status": "processed"}

@celery_app.task(name="generate_menu_summary")
def generate_menu_summary(results, restaurant_id: int):
    # `results` is list of group results
    return {
        "restaurant_id": restaurant_id,
        "processed_items": len(results),
        "items": results,
        "summary_generated_at": datetime.utcnow().isoformat()
    }

# ----- Public helpers -----
def create_restaurant_workflow(restaurant_data: dict):
    w = chain(
        create_restaurant_task.s(restaurant_data),
        sync_with_maps_api.s(),
        generate_qr_code.s(),
        send_welcome_notification.s(),
    )
    return w.apply_async()

def process_menu_batch(restaurant_id: int, menu_items: list[dict]):
    g = group([process_menu_item.s(restaurant_id, item) for item in menu_items])
    job = chord(g)(generate_menu_summary.s(restaurant_id))
    return job
