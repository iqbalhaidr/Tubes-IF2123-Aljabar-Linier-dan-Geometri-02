from fastapi import FastAPI,UploadFile,File,HTTPException
from typing import List
import numpy as np 
import process


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "backend running"}

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):


@app.post("upload_audio")
async def upload_audio(file: UploadFile = File(...)):