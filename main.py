from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import pickle
import logging

app = FastAPI()

# API Key setup
API_KEY = "mysecretkey"
api_key_header = APIKeyHeader(name="x-api-key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Schemas
class InputData(BaseModel):
    features: list

class OutputData(BaseModel):
    prediction: int

# Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Prediction API
@app.post("/predict", response_model=OutputData)
def predict(data: InputData, api_key: str = Security(api_key_header)):
    verify_api_key(api_key)

    prediction = model.predict([data.features]).tolist()[0]
    return {"prediction": prediction}