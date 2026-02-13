from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.routers import data, eda, features, training, evaluation, chat

app = FastAPI(title="FlowForge AI Backend", version="1.0.0")

# CORS (Allow UI to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(eda.router)
app.include_router(features.router)
app.include_router(training.router)
app.include_router(evaluation.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "FlowForge AI Backend is running"}  

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"mlflow": os.getenv("MLFLOW_TRACKING_URI"), "prefect": os.getenv("PREFECT_API_URL")}}

