from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import pandas as pd
from app.api.schemas import DataUploadResponse

router = APIRouter(prefix="/data", tags=["data"])

DATA_DIR = "app/data"
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(file: UploadFile = File(...)):
    try:
        file_location = f"{DATA_DIR}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read columns for immediate feedback
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_location, nrows=5)
        elif file.filename.endswith('.parquet'):
            df = pd.read_parquet(file_location) # parquet usually reads schema easily
            df = df.head(5)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Parquet.")

        return DataUploadResponse(
            filename=file.filename,
            filepath=file_location,
            columns=df.columns.tolist(),
            message="File uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
