# 🚨 RANSOMCHAT-API

A REST API built with **FastAPI** to expose conversations between ransomware groups and their victims, using JSON files hosted on GitLab.

---

## 📌 Objective

Create a REST API that serves ransomware group and victim discussions from JSON files, without creating or writing any files. The API is fully containerized with Docker and always returns JSON data.

---

## ✨ Features

- **Returns only JSON data**
- **Read-only:** Does not create or write files
- **Dockerized API**

---

## 📂 Data Source

Chat data is stored in publicly available JSON files hosted on [GitHub](https://github.com/Casualtek/Ransomchats).

---

## 🚦 Endpoints

### 1. `GET /api/groups`

List all groups and indicate the number of discussions for each.

#### Example response:
```json
{
  "groups": [
    { "name": "Akira", "total_chats": 51 },
    { "name": "Avaddon", "total_chats": 7 },
    { "name": "Conti", "total_chats": 32 }
  ]
}
```

---

### 2. `GET /api/groups/{group_name}/chats`

Display the chats of a given group with the date and the number of messages.

#### Example response:

```json
{
  "group": "Avaddon",
  "total_chats": 7,
  "chats": [
    { "date": "20210112", "messages_count": 25 },
    { "date": "20210324", "messages_count": 73 },
    { "date": "20210518_3", "messages_count": 103 }
  ]
}
```

---

### 3. `GET /api/groups/{group_name}/chats/{date}`

Provide the full content of a specific chat.

#### Example response:

```json
[
  {
    "sender": "Avaddon",
    "timestamp": "2021-05-18T14:01:00Z",
    "message": "Ready to decrypt your servers if payment is made."
  }
]
```

---

## 🗂️ Project Structure

```
app/
  ├─ main.py       # FastAPI entry point
  ├─ auth.py       # Middleware for api-key
  ├─ .env          # Environment variable management
Dockerfile
requirements.txt
README.md
```

---

## ⚙️ Technical Details

- **Language:** Python 3.13.3
- **Framework:** FastAPI
- **Containerization:** Docker

---

## 🚀 Installation & Usage

### ▶️ Local

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API:
   ```bash
   fastapi run
   ```

### 🐳 With Docker

1. Build the Docker image:
   ```bash
   docker build -t ransomchat-api .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 ransomchat-api
   ```

---

## 👥 Authors

Made by Miguel LOPES and Clément DUMAS

---