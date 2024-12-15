from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
from zipfile import ZipFile
from fastapi.middleware.cors import CORSMiddleware
from process import musicRetrieval, musicRetrievalDataset, ImageRetrieval
import json
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.mount("/datasetimage", StaticFiles(directory="datasetimage"), name="datasetimage")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_AUDIO = os.path.join(BASE_DIR, "datasetaudio")
DATASET_IMAGE = os.path.join(BASE_DIR, "datasetimage")
MAPPER_FILE = os.path.join(BASE_DIR, "mapper.json")
DB_AUDIO = os.path.join(BASE_DIR, "dbaudio.json")
QUERY_AUDIO = os.path.join(BASE_DIR, "query_audio.mid")
QUERY_IMAGE = os.path.join(BASE_DIR, "query_image.png")
RESULT_PATH = os.path.join(BASE_DIR, "result.json")

os.makedirs(DATASET_AUDIO, exist_ok=True)
os.makedirs(DATASET_IMAGE, exist_ok=True)


def is_json_empty(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    if os.path.getsize(file_path) == 0:
        return True
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            if data == {} or data == [] or data is None:
                print("Kosong jir")
                return True
            
            return False
        
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Invalid JSON in file {file_path}")



@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(BASE_DIR, "query_image.png")

        if os.path.exists(file_location):
            os.remove(file_location)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"message": "Image Uploaded successfully"}
    except Exception as e:
        return{"error": str(e)}

@app.post("/search_image/")
async def search_image():
    try:
        print("Proceeding with Image Retrieval...")
        ImageRetrieval(DATASET_IMAGE,QUERY_IMAGE,RESULT_PATH)
    except Exception as e:
        print("Gagal lagi")
        return{"error": str(e)}

@app.post("/search_audio/")
async def search_audio():
    try:
        print(f"Checking if {DB_AUDIO} is empty...")
        if is_json_empty(DB_AUDIO):
            print(f"{DB_AUDIO} is empty. Proceeding with musicRetrieval...")
            musicRetrieval(DATASET_AUDIO,QUERY_AUDIO,RESULT_PATH)
        else:
            print(f"{DB_AUDIO} exists. Proceeding with musicRetrievalDataset...")
            musicRetrievalDataset(DB_AUDIO,QUERY_AUDIO,RESULT_PATH)
        return {"message": "Search Audio successfully"}
    except Exception as e:
        print("Gagal jir")
        return{"error": str(e)}

@app.post("/upload_audio/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(BASE_DIR, "query_audio.mid")

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
