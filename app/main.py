# Import necessary modules
from fastapi import FastAPI, HTTPException, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import auth

#*#################################
#* Pydantic Models for API documentation
#*#################################

class Group(BaseModel):
    """Model representing a chat group"""
    name: str
    total_chats: int

class GroupsResponse(BaseModel):
    """Response model for groups endpoint"""
    last_updated: Optional[str] = None
    statistics: Optional[dict] = None
    groups: List[Group]

class Chat(BaseModel):
    """Model representing a chat within a group"""
    chat_id: str
    date: Optional[str] = None
    messages_count: int

class GroupChatsResponse(BaseModel):
    """Response model for group chats endpoint"""
    group: str
    total_chats: int
    chats: List[Chat]

#*#################################
#* FastAPI application configuration
#*#################################

# Create FastAPI app with API key validation and documentation
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    title="Chat Groups API",
    description="""
    API to retrieve information about chat groups and their messages.
    
    Features:
    * Get all available chat groups
    * Retrieve chats from specific groups
    * Get detailed content of individual chats
    
    Usage:
    Use this API to access chat data organized by groups. Each group contains multiple chats identified by unique IDs.
    """
)


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}


@app.get("/openapi.json", include_in_schema=False)
async def protected_openapi(api_key: str = Depends(auth.validate_docs_api_key)):
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


@app.get("/docs", include_in_schema=False)
async def protected_swagger(api_key: str = Depends(auth.validate_docs_api_key)):
    return get_swagger_ui_html(
        openapi_url=f"/openapi.json?api_key={api_key}",
        title=f"{app.title} - Swagger UI",
    )

#*#################################
#* Loading environment variables
#*#################################

load_dotenv()

# Retrieve the chat index URL from the .env file
URL_CHAT_INDEX = os.getenv("URL_CHAT_INDEX")


# Function: search
# Description: Performs a GET request on the provided URL and returns the response content as text.
# Parameters: url (str) - the URL to request
# Returns: The response content as a string if the request is successful, otherwise raises HTTPException
def search(url):
    try:
        # Perform GET request to the URL
        index = requests.get(url)
        content = index.text if index else None
        return content
    except Exception as e:
        # Handle any exception during the request
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")


# Route: /api/groups
# Description: Retrieves the list of groups and the total number of chats per group.
# Parameters: None
# Returns: JSON object with a list of groups and their chat counts.
@app.get(
    "/api/groups",
    response_model=GroupsResponse,
    summary="Get all groups",
    description="Retrieve the list of all available groups with their total number of chats.",
    tags=["Groups"],
    dependencies=[Depends(auth.validate_api_key)],
    responses={
        200: {
            "description": "List of groups retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "last_updated": "2025-06-01T12:00:00",
                        "statistics": {
                            "total_groups": 23,
                            "total_chats": 218,
                            "total_messages": 10699
                        },
                        "groups": [
                            {"name": "Akira", "total_chats": 150},
                            {"name": "Avos", "total_chats": 89}
                        ]
                    }
                }
            }
        },
        404: {"description": "No groups found"},
        500: {"description": "Server error - unable to load or parse data"}
    }
)
def get_groups():
    try:
        # Load and parse the chat index
        index = json.loads(search(URL_CHAT_INDEX))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading groups: {str(e)}")

    # Check if index exists
    if not index:
        raise HTTPException(status_code=404, detail="No groups found")

    try:
        # Extract group information
        groups = [
            {
                "name": group,
                "total_chats": index["groups"][group]["group_statistics"]["chat_count"],
            }
            for group in index["groups"]
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing group data: {str(e)}")

    return {
        "last_updated": index.get("last_updated", None),
        "statistics": index.get("statistics", None),
        "groups": groups
    }


# Route: /api/groups/{group_name}/chats
# Description: Retrieves the chats of a specific group.
# Parameters: group_name (str) - the name of the group
# Returns: JSON object with group name, total chats, and a list of chats (chat_id, date and message count).
@app.get(
    "/api/groups/{group_name}/chats",
    response_model=GroupChatsResponse,
    summary="Get a list of chats from a specific group",
    description="Retrieve all chats from a specific group with their IDs, dates, and message counts.",
    tags=["Chats"],
    dependencies=[Depends(auth.validate_api_key)],
    responses={
        200: {
            "description": "Chats retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "group": "Akira",
                        "total_chats": 150,
                        "chats": [
                            {
                                "chat_id": "20240601",
                                "date": "2024-06-01",
                                "messages_count": 45
                            },
                            {
                                "chat_id": "20240720",
                                "date": None,
                                "messages_count": 12
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "Group name is required"},
        404: {"description": "Group not found or no groups available"},
        500: {"description": "Server error - unable to load or parse data"}
    }
)
def get_groups_with_chats(group_name: str):
    # Validate input parameters
    if not group_name:
        raise HTTPException(status_code=400, detail="Group name is required")
    
    try:
        # Load and parse the chat index
        index = json.loads(search(URL_CHAT_INDEX))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat index: {str(e)}")
    
    # Check if index exists
    if not index:
        raise HTTPException(status_code=404, detail="No groups found")
    
    # Check if group exists
    if not group_name in str(index):
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found")
    
    try:
        # Extract group statistics
        total_chat_group = index["groups"][group_name]["group_statistics"]["chat_count"]
        chats = []
        
        # Process each chat in the group
        for chat in index["groups"][group_name]["chats"]:
            chat_id = chat["chat_id"]
            
            # Try to parse date from chat_id (format: YYYYMMDD)
            try:
                date = datetime.strptime(chat_id, "%Y%m%d").strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                # If parsing fails, set date to None
                date = None
            
            # Add chat information to the list
            chats.append({
                "chat_id": chat_id,
                "date": date,
                "messages_count": index.get("message_count", 0)  # Default to 0 if not available,
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing chats: {str(e)}")
    
    return {
        "group": group_name,
        "total_chats": total_chat_group,
        "chats": chats
    }


# Route: /api/groups/{group_name}/chats/{chat_id}
# Description: Retrieves the content of a specific chat from a group on a given chat_id.
# Parameters: group_name (str) - the name of the group; chat_id (str) - the chat id
# Returns: JSON object with the raw chat content.
@app.get(
    "/api/groups/{group_name}/chats/{chat_id}",
    summary="Get specific chat content",
    description="Retrieve the complete content of a specific chat from a group using the chat ID.",
    tags=["Chats"],
    dependencies=[Depends(auth.validate_api_key)],
    responses={
        200: {
            "description": "Chat content retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "chat_id": "20240601",
                        "messages": [
                            {
                                "party": "John",
                                "content": "Hello everyone!",
                                "timestamp": "2024-06-01T10:30:00"
                            }
                        ],
                        "metadata": {
                            "total_messages": 45,
                            "date": "2024-06-01"
                        }
                    }
                }
            }
        },
        400: {"description": "Group name and chat ID are required"},
        404: {"description": "Group not found or chat not found in the specified group"},
        500: {"description": "Server error - unable to load or parse data"}
    }
)
def get_chat(group_name: str, chat_id: str):
    # Validate input parameters
    if not group_name or not chat_id:
        raise HTTPException(status_code=400, detail="Group name and chat id are required")
    
    try:
        # Load and parse the chat index
        index = json.loads(search(URL_CHAT_INDEX))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat index: {str(e)}")
    
    # Check if group exists
    if not group_name in str(index):
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found")
    
    try:
        # Find the URL for the specific chat
        url_chat = next(
            (chat["raw_url"] for chat in index["groups"][group_name]["chats"] if chat["chat_id"] == chat_id),
            None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching chat url: {str(e)}")
    
    # Check if chat exists
    if not url_chat:
        raise HTTPException(status_code=404, detail=f"Chat with id '{chat_id}' not found in group '{group_name}'")
    
    try:
        # Fetch and parse the chat content
        result_chat = json.loads(search(url_chat))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat content: {str(e)}")
    
    #TODO: Ajouter les métadonnées du chat (date et nombre de messages)
     # Try to parse date from chat_id (format: YYYYMMDD)
    try:
        date = datetime.strptime(chat_id, "%Y%m%d").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        # If parsing fails, set date to None
        date = None

    try:
        # Add metadata information to the dict
        result_chat["metadata"] = {
            "date": date,
            "messages_count": len(result_chat.get("messages", []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding metadata to chat: {str(e)}")
        
    return result_chat
