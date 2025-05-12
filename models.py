from pydantic import BaseModel

class Service(BaseModel):
    name: str
    type: str
    location: str
    address: str
    mobile_no: str
    timings: str
    cost: str
    available: bool
