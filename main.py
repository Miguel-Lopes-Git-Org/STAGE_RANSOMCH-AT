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
# Returns: The response content as a string if the request is successful, otherwise None.
def search(url):
    result = requests.get(url)
    content = result.text if result else None
    return content

@app.get("/api/groups")
# Route: /api/groups
# Description: Retrieves the list of groups and the total number of chats per group.
# Parameters: None
# Returns: JSON object with a list of groups and their chat counts.
def get_groups():
    result = json.loads(search(URL_CHAT_INDEX))
    groups = [
        {
            "name": group,
            "total_chats": result["groups"][group]["group_statistics"]["chat_count"],
        }
        for group in result["groups"]
    ]

    return {
        "groups": groups
    }

@app.get("/api/groups/{group_name}/chats")
# Route: /api/groups/{group_name}/chats
# Description: Retrieves the chats of a specific group.
# Parameters: group_name (str) - the name of the group
# Returns: JSON object with group name, total chats, and a list of chats (id_chat, date and message count).
def get_groups_with_chats(group_name):

    result = json.loads(search(URL_CHAT_INDEX))  # Retrieve the chat index

    # Check if the group exists in the index
    if group_name in str(result):
        print("Group found")
    else:
        print("Group not found")
    # Total number of chats in the group

    total_chat_group = result["groups"][group_name]["group_statistics"]["chat_count"]
    # List of chats in the group with formatted date and message count
    chats = []
    for chat in result["groups"][group_name]["chats"]:
        chat_id = chat["chat_id"]
        try:
            date = datetime.strptime(chat_id, "%Y%m%d").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            date = None
        chats.append({
            "id_chat": chat_id,
            "date": date,
            "messages_count": chat["message_count"],
        })

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

    result = json.loads(search(URL_CHAT_INDEX))  # Retrieve the chat index

    # Check if the group exists in the index
    if group_name in str(result):
        print("Group found")
    else:
        print("Group not found")

    # Search for the raw chat URL corresponding to the id_chat
    url_chat = next(
        (chat["raw_url"] for chat in result["groups"][group_name]["chats"] if chat["chat_id"] == id_chat),
        None
    )
    # Retrieve the chat content
    result_chat = search(url_chat)

    return {
        result_chat
    }