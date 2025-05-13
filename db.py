from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from models import Service
import uuid

client = QdrantClient(host="localhost", port=6333)  # Assuming Qdrant is running locally

COLLECTION_NAME = "services"

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=2, distance=Distance.EUCLID),
)

def insert_services(services: list[Service]):
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[s.latitude, s.longitude],
            payload=s.dict()
        )
        for s in services
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def search_nearby(lat: float, lon: float, top_k: int = 5):
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=[lat, lon],
        limit=top_k
    )
    return [hit.payload for hit in hits]
