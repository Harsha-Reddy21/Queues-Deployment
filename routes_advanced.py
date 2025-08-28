from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from celery.result import AsyncResult
from datetime import datetime

from celery_app import celery_app
from tasks import analyze_menu_performance, bulk_menu_update, process_menu_images
from workflows import create_restaurant_workflow, process_menu_batch

router_adv = APIRouter()

# ----- Schemas -----
class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DateRange(BaseModel):
    start: str
    end: str

class MenuUpdate(BaseModel):
    item_id: int
    price: Optional[float] = None
    available: Optional[bool] = None

class MenuBatch(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)

# ----- Workflows -----
@router_adv.post("/workflows/restaurant-setup/{restaurant_id}")
def start_restaurant_setup(restaurant_id: int):
    wf = create_restaurant_workflow({"id": restaurant_id, "name": f"R-{restaurant_id}"})
    return {"workflow_id": wf.id}

@router_adv.get("/workflows/{workflow_id}/status")
def workflow_status(workflow_id: str):
    res = AsyncResult(workflow_id, app=celery_app)
    meta = res.info if isinstance(res.info, dict) else {}
    return {
        "workflow_id": workflow_id,
        "status": res.status,
        "result": res.result if res.successful() else None,
        "meta": meta,
        "error": str(res.result) if res.failed() else None,
    }

@router_adv.post("/workflows/menu-batch-process/{restaurant_id}")
def workflow_menu_batch(restaurant_id: int, payload: MenuBatch):
    job = process_menu_batch(restaurant_id, payload.items)
    return {"workflow_id": job.id}

# ----- Advanced tasks -----
@router_adv.post("/analytics/menu/{restaurant_id}")
def start_menu_analytics(restaurant_id: int, date_range: DateRange):
    task = analyze_menu_performance.delay(restaurant_id, date_range.dict())
    return {"task_id": task.id}

@router_adv.post("/menu/bulk-update/{restaurant_id}")
def start_bulk_menu_update(restaurant_id: int, updates: List[MenuUpdate]):
    task = bulk_menu_update.apply_async(args=[restaurant_id, [u.dict() for u in updates]], queue="q.medium")
    return {"task_id": task.id}

@router_adv.post("/menu/{menu_item_id}/images")
def start_menu_images(menu_item_id: int, image_urls: List[str]):
    task = process_menu_images.apply_async(args=[menu_item_id, image_urls], queue="q.images")
    return {"task_id": task.id}

# ----- Task utilities -----
@router_adv.get("/tasks/status/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    info = res.info if isinstance(res.info, dict) else {}
    return TaskStatus(
        task_id=task_id,
        status=res.status,
        progress=info.get("progress", 0),
        result=res.result if res.successful() else None,
        error=str(res.result) if res.failed() else None,
    )

@router_adv.get("/tasks/priority/{priority_level}")
def list_by_priority(priority_level: str):
    # This endpoint is illustrative; Celery does not expose a queue browser by default without broker APIs.
    # We return the known queues that match.
    mapping = {"high": "q.high", "medium": "q.medium", "low": "q.low", "images": "q.images", "analytics": "q.analytics"}
    q = mapping.get(priority_level.lower())
    if not q:
        raise HTTPException(status_code=404, detail="Unknown priority/queue.")
    return {"queue": q, "note": "Use Flower to inspect live tasks in this queue."}

@router_adv.post("/tasks/{task_id}/retry")
def retry_failed_task(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    if res.state not in ("FAILURE",):
        raise HTTPException(status_code=400, detail=f"Task not in FAILURE (state={res.state}).")
    # Re-queue using stored args/kwargs if backend has them
    if not res.result or not hasattr(res.result, "request"):
        raise HTTPException(status_code=422, detail="Cannot recover original args/kwargs for retry.")
    # Fallback: ask client to rerun with same args via the original endpoint
    raise HTTPException(status_code=501, detail="Server-side retry not implemented. Please re-trigger the task.")

# Simple in-memory counters for demo analytics
_task_counters = {"started": 0, "succeeded": 0, "failed": 0}

@router_adv.get("/analytics/task-performance")
def task_performance():
    # NOTE: for production, push counters to Prometheus or statsd
    return _task_counters
