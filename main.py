from fastapi import FastAPI, UploadFile, File, Query
from db import insert_services, search_nearby
from utils import parse_csv, extract_location_and_service
from models import Service
import requests
from geopy.distance import geodesic

app = FastAPI()

@app.post("/add_service/")
async def add_service(service: Service):
    insert_services([service])
    return {"message": "Service added successfully."}


@app.post("/upload_services/")
async def upload(file: UploadFile = File(...)):
    services = parse_csv(file)
    insert_services(services)
    return {"message": f"{len(services)} services uploaded successfully."}


@app.get("/get_help/")
def get_help(query: str = Query(..., description="Emergency message from user")):
    location, service_keyword = extract_location_and_service(query)

    if not location:
        return {"error": "Location not found in message."}

    geo_resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location, "format": "json", "limit": 1},
        headers={"User-Agent": "EmergencyLocator/1.0"}
    )
    geo_data = geo_resp.json()
    if not geo_data:
        return {"error": f"Location '{location}' not found."}

    lat, lon = float(geo_data[0]['lat']), float(geo_data[0]['lon'])
    results = search_nearby(lat, lon, top_k=100)

    # Filter by radius (e.g., 10km)
    radius_km = 10
    filtered_by_radius = [
        r for r in results
        if geodesic((lat, lon), (r['latitude'], r['longitude'])).km <= radius_km
    ]

    if service_keyword:
        filtered = [r for r in filtered_by_radius if service_keyword.lower() in r.get('type', '').lower()]
    else:
        filtered = filtered_by_radius

    return {
        "original_message": query,
        "detected_location": location,
        "coordinates": [lat, lon],
        "detected_service": service_keyword or "not specified",
        "nearby_help": filtered
    }
