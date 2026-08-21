Python
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 프론트엔드 통신 허용 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    id: str
    category: str
    title: str
    highlight: Optional[str] = ""
    fact1: Optional[str] = ""
    fact2: Optional[str] = ""
    fact3: Optional[str] = ""
    fact4: Optional[str] = ""
    summary: Optional[str] = ""
    image: Optional[str] = ""
    source: Optional[str] = ""
    action_text: Optional[str] = "갈래? 초대 💌"
    action_color: Optional[str] = "bg-[#FEE500] text-[#191919]"
    tags: Optional[str] = ""

def init_db():
    conn = sqlite3.connect("portal.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            category TEXT,
            title TEXT,
            highlight TEXT,
            fact1 TEXT,
            fact2 TEXT,
            fact3 TEXT,
            fact4 TEXT,
            summary TEXT,
            image TEXT,
            source TEXT,
            action_text TEXT,
            action_color TEXT,
            tags TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# [핵심] 프론트엔드가 데이터를 가져가는 GET 엔드포인트
@app.get("/api/items")
def get_items():
    conn = sqlite3.connect("portal.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items ORDER BY rowid DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 크롤러가 데이터를 집어넣는 POST 엔드포인트
@app.post("/api/items")
def create_item(item: Item):
    conn = sqlite3.connect("portal.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO items 
            (id, category, title, highlight, fact1, fact2, fact3, fact4, summary, image, source, action_text, action_color, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.id, item.category, item.title, item.highlight,
            item.fact1, item.fact2, item.fact3, item.fact4,
            item.summary, item.image, item.source, item.action_text,
            item.action_color, item.tags
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {"status": "success", "id": item.id}
