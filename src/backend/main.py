from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
from zipfile import ZipFile
from fastapi.middleware.cors import CORSMiddleware
from process import musicRetrieval, musicRetrievalDataset, ImageRetrieval, wav_to_midi
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import rarfile

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


@app.get("/result")
async def get_result():
    try:
        # Open and read the result.json file
        with open(RESULT_PATH, "r") as f:
            result_data = json.load(f)
        return JSONResponse(content=result_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/mapper")
async def get_mapper():
    try:
        # Open and read the mapper.json file
        with open(MAPPER_FILE, "r") as f:
            mapper_data = json.load(f)
        return JSONResponse(content=mapper_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/combined_image")
async def get_combined_data():
    try:
        # Load result.json data
        with open(RESULT_PATH, "r") as f:
            result_data = json.load(f)

        # Load mapper.json data
        with open(MAPPER_FILE, "r") as f:
            mapper_data = json.load(f)

        combined_data = []
        
        # Combine logic (just an example)
        for result_item in result_data[:-1]:  # Exclude the last item (execution time)
            matched_mapper = next((mapper for mapper in mapper_data if mapper["pic_name"] == result_item["file"]), None)
            if matched_mapper:
                combined_item = {
                    "audio_file": matched_mapper["audio_file"],
                    "pic_name": result_item["file"],
                    "sim": result_item["sim"]
                }
                combined_data.append(combined_item)

        execution_time = result_data[-1]["execution"] if result_data else None
        
        return JSONResponse(content={"data": combined_data, "execution_time": execution_time})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.get("/combined_audio")
async def get_combined_data():
    try:
        # Load result.json data
        with open(RESULT_PATH, "r") as f:
            result_data = json.load(f)

        # Load mapper.json data
        with open(MAPPER_FILE, "r") as f:
            mapper_data = json.load(f)

        combined_data = []
        
        # Combine logic (just an example)
        for result_item in result_data[:-1]:  # Exclude the last item (execution time)
            matched_mapper = next((mapper for mapper in mapper_data if mapper["audio_file"] == result_item["name"]), None)
            if matched_mapper:
                combined_item = {
                    "audio_file": result_item["name"],
                    "pic_name": matched_mapper["pic_name"],
                    "sim": result_item["sim"]
                }
                combined_data.append(combined_item)

        execution_time = result_data[-1]["execution"] if result_data else None
        
        return JSONResponse(content={"data": combined_data, "execution_time": execution_time})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
        if not os.path.exists(QUERY_IMAGE):
            return {"message": "Cannot search, file does not exist."}
        print("Proceeding with Image Retrieval...")
        ImageRetrieval(DATASET_IMAGE,QUERY_IMAGE,RESULT_PATH)

        if os.path.exists(QUERY_IMAGE):
            os.remove(QUERY_IMAGE)
            print(f"File {QUERY_IMAGE} has been removed.")
        else:
            print(f"File {QUERY_IMAGE} not found, nothing to remove.")
        
        return {"message": "Search Image successfully"}
    except Exception as e:
        print("Gagal lagi")
        return{"error": str(e)}

@app.post("/search_audio/")
async def search_audio():
    try:
        for file_name in os.listdir(DATASET_AUDIO):
            file_path = os.path.join(DATASET_AUDIO, file_name)
            if file_name.endswith(".wav"):
                midi_output_path = os.path.join(DATASET_AUDIO, file_name.replace(".wav", ".mid"))
                print(f"Converting {file_name} to MIDI...")
                wav_to_midi(file_path, midi_output_path)
                print(f"{file_name} converted to MIDI at {midi_output_path}")
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Removed original WAV file: {file_path}")
        
        if not os.path.exists(QUERY_AUDIO):
            return {"error": "Cannot search, file does not exist."}

        print(f"Checking if {DB_AUDIO} is empty...")
        if is_json_empty(DB_AUDIO):
            print(f"{DB_AUDIO} is empty. Proceeding with musicRetrieval...")
            musicRetrieval(DATASET_AUDIO, QUERY_AUDIO, RESULT_PATH)
        else:
            print(f"{DB_AUDIO} exists. Proceeding with musicRetrievalDataset...")
            musicRetrievalDataset(DB_AUDIO, QUERY_AUDIO, RESULT_PATH)
        
        if os.path.exists(QUERY_AUDIO):
            os.remove(QUERY_AUDIO)
            print(f"File {QUERY_AUDIO} has been removed.")
        else:
            print(f"File {QUERY_AUDIO} not found, nothing to remove.")
        
        return {"message": "Search Audio successfully"}
    except Exception as e:
        print("Gagal jir")
        return{"error": str(e)}

@app.post("/upload_audio/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_extension = os.path.splitext(file.filename)[1].lower()

        file_location = os.path.join(BASE_DIR, "query_audio.mid")
        temp_wav_path = os.path.join(BASE_DIR, "temp_audio.wav")

        if os.path.exists(file_location):
            os.remove(file_location)

        if file_extension == ".wav":
            with open(temp_wav_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            wav_to_midi(temp_wav_path, file_location)
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

        elif file_extension == ".mid":
            # Save the MIDI file directly
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        else:
            return {"error": "Unsupported file format. Only .wav and .mid are allowed."}

        return {"message": "Audio uploaded successfully"}
    except Exception as e:
        return{"error": str(e)}

import os
import shutil
from fastapi import UploadFile, File, Form
from zipfile import ZipFile
import rarfile

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), file_type: str = Form(...)):
    try:
        def clear_existing_files(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        if file_type == "audio":
            clear_existing_files(DATASET_AUDIO)

            file_location = os.path.join(BASE_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            if file.filename.endswith('.zip'):
                with ZipFile(file_location, 'r') as zip_ref:
                    zip_ref.extractall(DATASET_AUDIO)
            elif file.filename.endswith('.rar'):
                with rarfile.RarFile(file_location, 'r') as rar_ref:
                    rar_ref.extractall(DATASET_AUDIO)
            else:
                return {"error": "Unsupported file format. Please upload a zip or rar file."}

            os.remove(file_location)  # Clean up the uploaded ZIP/RAR file
            return {"message": "Audio file extracted successfully"}

        elif file_type == "pictures":
            clear_existing_files(DATASET_IMAGE)

            file_location = os.path.join(BASE_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            if file.filename.endswith('.zip'):
                with ZipFile(file_location, 'r') as zip_ref:
                    zip_ref.extractall(DATASET_IMAGE)
            elif file.filename.endswith('.rar'):
                with rarfile.RarFile(file_location, 'r') as rar_ref:
                    rar_ref.extractall(DATASET_IMAGE)
            else:
                return {"error": "Unsupported file format. Please upload a zip or rar file."}

            os.remove(file_location)  # Clean up the uploaded ZIP/RAR file
            return {"message": "Pictures file extracted successfully"}

        elif file_type == "mapper":
            with open(MAPPER_FILE, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return {"message": "Mapper file uploaded successfully"}

        else:
            return {"error": "Invalid file type"}

    except Exception as e:
        return {"error": str(e)}
