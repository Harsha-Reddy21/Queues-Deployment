from celery_app import celery_app
from datetime import datetime
from typing import List, Dict
import time, random

# ========= ANALYTICS =========
@celery_app.task(bind=True, name="analyze_menu_performance", rate_limit="10/m", autoretry_for=(Exception,), retry_backoff=2, retry_backoff_max=60, retry_jitter=True, max_retries=5)
def analyze_menu_performance(self, restaurant_id: int, date_range: dict):
    # Simulate multi-step pipeline with progress updates
    # Step 1: Gather menu item data (25%)
    self.update_state(state="PROGRESS", meta={"progress": 25, "step": "gather"})
    time.sleep(1)
    items = [{"id": i, "name": f"Item {i}", "sales": random.randint(1, 100), "price": random.uniform(100, 500)} for i in range(1, 21)]

    # Step 2: Calculate popularity metrics (50%)
    self.update_state(state="PROGRESS", meta={"progress": 50, "step": "metrics"})
    time.sleep(1)
    top_items = sorted(items, key=lambda x: x["sales"], reverse=True)[:5]
    avg_sales = sum(i["sales"] for i in items) / len(items)

    # Step 3: Generate pricing recommendations (75%)
    self.update_state(state="PROGRESS", meta={"progress": 75, "step": "pricing"})
    time.sleep(1)
    recommendations = []
    for i in items:
        # simple heuristic: if sales high, slight price increase; else small decrease
        delta = 0.05 if i["sales"] > avg_sales else -0.03
        new_price = round(i["price"] * (1 + delta), 2)
        recommendations.append({"item_id": i["id"], "old_price": round(i["price"], 2), "recommended_price": new_price})

    # Step 4: Create performance report (100%)
    self.update_state(state="PROGRESS", meta={"progress": 100, "step": "report"})
    report = {
        "restaurant_id": restaurant_id,
        "date_range": date_range,
        "top_items": top_items,
        "average_sales": round(avg_sales, 2),
        "recommendations": recommendations,
        "generated_at": datetime.utcnow().isoformat()
    }
    return report


# ========= BATCH MENU OPS =========
@celery_app.task(name="bulk_menu_update", rate_limit="60/m", autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3)
def bulk_menu_update(restaurant_id: int, updates: List[dict]):
    # Pretend to update DB + cache + search index
    # Each update: {"item_id": int, "price": float|None, "available": bool|None}
    results = []
    for u in updates:
        time.sleep(0.1)
        changed = {}
        if "price" in u and u["price"] is not None:
            changed["price"] = u["price"]
        if "available" in u and u["available"] is not None:
            changed["available"] = u["available"]
        # TODO: persist to DB, invalidate Redis cache, update search index
        results.append({"item_id": u["item_id"], "applied": changed})
    return {"restaurant_id": restaurant_id, "updated_count": len(results), "details": results}


# ========= MENU IMAGES =========
@celery_app.task(name="process_menu_images", rate_limit="30/m", autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=5)
def process_menu_images(menu_item_id: int, image_urls: List[str]):
    # Simulate download + transform
    processed = []
    for url in image_urls:
        time.sleep(0.3)
        processed.append({
            "original_url": url,
            "optimized_url": f"{url}?optimized=1",
            "thumbnail_url": f"{url}?thumb=1",
        })
    # TODO: save references in DB, update cache
    return {"menu_item_id": menu_item_id, "processed_images": processed}
