from fastapi import FastAPI, UploadFile, File
import csv, io
from db import add_service, search_nearby
from models import Service

app = FastAPI(title="🆘 Emergency Service API")

@app.post("/add/")
def add_single_service(service: Service):
    add_service(service)
    return {"msg": f"{service.type} '{service.name}' saved!"}

@app.post("/file_upload/")
def bulk_upload(file: UploadFile = File(...)):
    content = file.file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    count = 0  
    for row in csv_reader:
        try:
            service = Service(**row)
            add_service(service)
            count += 1
        except Exception as e:
            print(f"❌ Failed row: {row} → {e}")
    return {"msg": f"{count} services uploaded successfully."}

@app.get("/find_help/")
def find_services(location: str):
    results = search_nearby(location)
    return {
        "your_location": location,
        "nearby_services": results
    }
