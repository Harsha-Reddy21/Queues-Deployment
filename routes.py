from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from celery_app import celery_app
from tasks import generate_restaurant_report, sync_restaurant_data
import crud, schemas, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Restaurant CRUD
@router.post("/restaurants/", response_model=schemas.RestaurantOut)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    return crud.create_restaurant(db, restaurant)

@router.get("/restaurants/", response_model=list[schemas.RestaurantOut])
def list_restaurants(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_restaurants(db, skip, limit)

# Celery Tasks
@router.post("/tasks/generate-report/{cuisine_type}")
def start_report(cuisine_type: str):
    task = generate_restaurant_report.delay(cuisine_type)
    return {"task_id": task.id}

@router.get("/tasks/status/{task_id}")
def get_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    response = {
        "task_id": task.id,
        "status": task.status,
        "progress": task.info.get("progress") if isinstance(task.info, dict) else None,
        "result": task.result if task.successful() else None,
        "error": str(task.result) if task.failed() else None
    }
    return response

@router.post("/restaurants/{restaurant_id}/sync")
def sync_data(restaurant_id: int):
    task = sync_restaurant_data.delay(restaurant_id)
    return {"task_id": task.id}

@router.get("/workers/status")
def workers_status():
    return {"workers": "Running"}
