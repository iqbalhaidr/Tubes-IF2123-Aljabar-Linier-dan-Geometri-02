from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
from zipfile import ZipFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_AUDIO = os.path.join(BASE_DIR, "datasetaudio")
DATASET_IMAGE = os.path.join(BASE_DIR, "datasetimage")
MAPPER_FILE = os.path.join(BASE_DIR, "mapper.json")

os.makedirs(DATASET_AUDIO, exist_ok=True)
os.makedirs(DATASET_IMAGE, exist_ok=True)

@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_parts = file.filename.rsplit('.', 1)
        file_extension = file_parts[-1].lower()
        file_location = os.path.join(BASE_DIR, f"query_image.{file_extension}")

        if os.path.exists(file_location):
            os.remove(file_location)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"message": "Image Uploaded successfully"}
    except Exception as e:
        return{"error": str(e)}

@app.post("/upload_audio/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_parts = file.filename.rsplit('.', 1)
        file_extension = file_parts[-1].lower()
        file_location = os.path.join(BASE_DIR, f"query_audio.{file_extension}")

        if os.path.exists(file_location):
            os.remove(file_location)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"message": "Image Uploaded successfully"}
    except Exception as e:
        return{"error": str(e)}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), file_type: str = Form(...)):
    try:
        if file_type == "audio":
            for file_name in os.listdir(DATASET_AUDIO):
                file_path = os.path.join(DATASET_AUDIO, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            file_location = os.path.join(BASE_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            with ZipFile(file_location, 'r') as zip_ref:
                zip_ref.extractall(DATASET_AUDIO)
            
            os.remove(file_location)  # Clean up the uploaded ZIP file
            return {"message": "Audio ZIP extracted successfully"}

        elif file_type == "pictures":
            for file_name in os.listdir(DATASET_IMAGE):
                file_path = os.path.join(DATASET_IMAGE, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            file_location = os.path.join(BASE_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            with ZipFile(file_location, 'r') as zip_ref:
                zip_ref.extractall(DATASET_IMAGE)
            
            os.remove(file_location)  # Clean up the uploaded ZIP file
            return {"message": "Pictures ZIP extracted successfully"}

        elif file_type == "mapper":
            # Write JSON content to mapper.json
            with open(MAPPER_FILE, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return {"message": "Mapper file uploaded successfully"}

        else:
            return {"error": "Invalid file type"}
    except Exception as e:
        return {"error": str(e)}
