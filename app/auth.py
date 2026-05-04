from fastapi import HTTPException, Security
from fastapi.security import api_key
from starlette import status
from dotenv import load_dotenv
import os

load_dotenv()

# Get the API key from the header
api_key_header = api_key.APIKeyHeader(name="X-API-KEY")

async def validate_api_key(key: str = Security(api_key_header)):
    # Validate the API key against the environment variable
    if key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized - API Key is wrong"
        )
    
    # If the API key is valid, return None
    return None
