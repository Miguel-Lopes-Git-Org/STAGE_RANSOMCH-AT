# Import necessary modules
from fastapi import FastAPI, HTTPException
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

#*#################################
#* FastAPI application configuration
#*#################################

app = FastAPI()

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
    """
    Fetch content from a given URL using HTTP GET request.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        str: The response content as text
        
    Raises:
        HTTPException: 500 error if the request fails
    """
    try:
        # Perform GET request to the URL
        index = requests.get(url)
        content = index.text if index else None
        return content
    except Exception as e:
        # Handle any exception during the request
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")


@app.get("/api/groups")
# Route: /api/groups
# Description: Retrieves the list of groups and the total number of chats per group.
# Parameters: None
# Returns: JSON object with a list of groups and their chat counts.
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
        "groups": groups
    }


@app.get("/api/groups/{group_name}/chats")
# Route: /api/groups/{group_name}/chats
# Description: Retrieves the chats of a specific group.
# Parameters: group_name (str) - the name of the group
# Returns: JSON object with group name, total chats, and a list of chats (id_chat, date and message count).
def get_groups_with_chats(group_name):
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
                "id_chat": chat_id,
                "date": date,
                "messages_count": chat["message_count"],
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing chats: {str(e)}")
    
    return {
        "group": group_name,
        "total_chats": total_chat_group,
        "chats": chats
    }


@app.get("/api/groups/{group_name}/chats/{id_chat}")
# Route: /api/groups/{group_name}/chats/{id_chat}
# Description: Retrieves the content of a specific chat from a group on a given id_chat.
# Parameters: group_name (str) - the name of the group; id_chat (str) - the chat id
# Returns: JSON object with the raw chat content.
def get_chat(group_name, id_chat):
    # Validate input parameters
    if not group_name or not id_chat:
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
            (chat["raw_url"] for chat in index["groups"][group_name]["chats"] if chat["chat_id"] == id_chat),
            None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching chat url: {str(e)}")
    
    # Check if chat exists
    if not url_chat:
        raise HTTPException(status_code=404, detail=f"Chat with id '{id_chat}' not found in group '{group_name}'")
    
    try:
        # Fetch and parse the chat content
        result_chat = json.loads(search(url_chat))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat content: {str(e)}")
    
    return result_chat