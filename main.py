from fastapi import FastAPI
from routes_advanced import router_adv

app = FastAPI(title="Queues-Deployment V2")
app.include_router(router_adv)
