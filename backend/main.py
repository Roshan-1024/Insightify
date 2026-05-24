from fastapi import FastAPI
from routes import router

app = FastAPI(title="Insightify App")
app.include_router(router)
