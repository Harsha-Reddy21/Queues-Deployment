from fastapi import FastAPI
import models, database
from routes import router

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Zomato-like with Celery")
app.include_router(router)
