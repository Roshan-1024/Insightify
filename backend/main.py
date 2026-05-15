from fastapi import FastAPI
from backend.routes import router

app = FastAPI(title="Insightify App")
app.include_router(router)
