from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from uuid import uuid4
import sqlite3
import json
import os

# ----------------------------
# Config
# ----------------------------
DB_PATH = "chat.db"
JSON_PATH = "chats.json"

# ----------------------------
# App init
# ----------------------------
app = FastAPI(title="Mini ChatGPT 6.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------------------
# Database setup
# ----------------------------
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        user_message TEXT,
        bot_reply TEXT
    )
    """)
    conn.commit()
    conn.close()

# ----------------------------
# Helper functions
# ----------------------------
def save_chat_db(session_id, user_msg, bot_reply):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (session_id, user_message, bot_reply) VALUES (?, ?, ?)",
                   (session_id, user_msg, bot_reply))
    conn.commit()
    conn.close()

def save_chat_json(session_id, user_msg, bot_reply):
    try:
        with open(JSON_PATH, "r") as f:
            data = json.load(f)
    except:
        data = {}
    if session_id not in data:
        data[session_id] = []
    data[session_id].append({"user": user_msg, "bot": bot_reply})
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_reply(session_id, message):
    msg_lower = message.lower()
    reply = None

    # Simple self-learning: check last similar messages in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT bot_reply FROM chat_history WHERE user_message LIKE ?", (f"%{msg_lower}%",))
    row = cursor.fetchone()
    if row:
        reply = row[0]
    else:
        reply = f"তুমি বলেছ: {message}"  # Default echo reply
    conn.close()

    # Save to DB and JSON
    save_chat_db(session_id, message, reply)
    save_chat_json(session_id, message, reply)

    return reply

# ----------------------------
# Routes
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat(message: str = Form(...), session_id: str = Form("")):
    if not session_id:
        session_id = str(uuid4())
    reply = get_reply(session_id, message)
    return {"reply": reply, "session_id": session_id}
