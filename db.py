from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
from models import Service

client = QdrantClient(host="localhost", port=6333)  
COLLECTION = "emergency_services"
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_collection():
    try:
        client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION}' created or recreated successfully.")
    except Exception as e:
        print(f"Error creating collection: {e}")

def add_service(service: Service):
    vector = model.encode(service.location).tolist()

    point = PointStruct(
        id=hash(service.name + service.location),
        vector=vector,
        payload=service.dict()  # Convert service data to dict (make sure Service model has a 'dict' method)
    )

    client.upsert(collection_name=COLLECTION, points=[point])
    print(f"Service '{service.name}' added successfully!")

def search_nearby(location: str, limit: int = 5):
    vector = model.encode(location).tolist()

    results = client.search(collection_name=COLLECTION, query_vector=vector, limit=limit)

    return [r.payload for r in results]
create_collection()


