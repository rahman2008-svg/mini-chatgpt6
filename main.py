from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uuid
import sqlite3

app = FastAPI(title="Mini ChatGPT 6.0")

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "chat_history.db"

# Table create
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_message TEXT,
    bot_reply TEXT
)
""")
conn.commit()
conn.close()

# Save chat
def save_chat(session_id, user_message, bot_reply):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (session_id, user_message, bot_reply) VALUES (?, ?, ?)",
                   (session_id, user_message, bot_reply))
    conn.commit()
    conn.close()

# Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat API
@app.post("/chat")
def chat(message: str = Form(...), session_id: str = Form("")):
    # session_id generate
    if not session_id:
        session_id = str(uuid.uuid4())

    # Simple reply (self-learning logic)
    msg_lower = message.lower()
    reply = None

    # Check DB for similar messages
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT bot_reply FROM chat_history WHERE user_message LIKE ?", (f"%{msg_lower}%",))
    row = cursor.fetchone()
    if row:
        reply = row[0]
    else:
        reply = f"তুমি বলেছ: {message}"

    conn.close()

    # Save chat
    save_chat(session_id, message, reply)

    return {"reply": reply, "session_id": session_id}
