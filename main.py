import sqlite3
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Visual Search API")

# 프론트엔드 연동을 위한 전체 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "visual_portal.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        category TEXT,
        title TEXT,
        image TEXT,
        highlight TEXT,
        fact1 TEXT,
        fact2 TEXT,
        fact3 TEXT,
        fact4 TEXT,
        summary TEXT,
        action_text TEXT,
        action_color TEXT,
        source TEXT,
        tags TEXT
    )
    """)
    conn.commit()

    # 초기 데이터 5건 자동 생성
    cur.execute("SELECT COUNT(*) FROM items")
    if cur.fetchone()[0] == 0:
        samples = [
            ("1", "IT/테크", "아이폰 16 프로 (iPhone 16 Pro)", 
             "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800",
             "출고가 155만원~", "⚖️ 무게: 199g", "⚡️ 칩셋: A18 Pro", "📸 5배 광학 줌", "🔋 최대 27시간 재생",
             "전용 캡처 버튼 탑재 및 역대 최소 베젤 플래그십", "살래? 최저가 비교 🛒", "bg-blue-600", "공식 스펙", "아이폰,애플,스펙,스마트폰"),
            ("2", "청년정책", "2026 청년 월세 특별지원 2차", 
             "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800",
             "월 최대 20만원 지원", "👤 만 19~34세 무주택", "💰 중위소득 60% 이하", "🏠 보증금 5천/월세 70이하", "🗓️ 복지로 상시 접수",
             "최대 12개월간 월세를 실지급하는 국토부 주거안정 정책", "신청할래? 자격확인 📝", "bg-emerald-600", "국토교통부", "월세,청년,지원금,복지,주거"),
            ("3", "여행/코스", "제주도 동쪽 감성 1박 2일 코스", 
             "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800",
             "1인 예상경비 18만원", "📍 1일: 함덕→비밀의숲→세화", "📍 2일: 성산일출봉→광치기", "🚗 렌터카 추천", "📸 세화 일몰 오션뷰",
             "에메랄드빛 해변 드라이브와 숲속 힐링을 묶은 최적 동선", "갈래? 친구 초대 💌", "bg-[#FEE500] text-[#191919]", "여행큐레이션", "제주도,여행,코스,1박2일,드라이브"),
            ("4", "맛집/카페", "성수동 웨이팅 없는 베이커리 팝업", 
             "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800",
             "소금빵 3,800원~", "🥐 트러플 명란 소금빵", "⏰ 평일 14시 대기 0분", "🚗 공영주차장 권장", "📍 성수역 3번출구 도보5분",
             "당일 생산 천연발효 빵을 파는 감성 골목 숨은 맛집", "갈래? 친구 초대 💌", "bg-[#FEE500] text-[#191919]", "서울맛집", "성수동,베이커리,카페,소금빵,맛집"),
            ("5", "축제/행사", "2026 청주 달콤상생 딸기축제", 
             "https://images.unsplash.com/photo-1518635017480-d471b405533f?w=800",
             "무료입장 (D-12)", "🗓️ 03.28 ~ 03.29", "📍 청주 문화제조창 광장", "🍓 직거래 장터 운영", "🚗 주차 2시간 무료",
             "신선한 딸기 직거래 장터와 케이크 만들기 체험 부스", "갈래? 친구 초대 💌", "bg-[#FEE500] text-[#191919]", "청주시", "딸기,축제,청주,무료,문화제조창")
        ]
        cur.executemany("INSERT INTO items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", samples)
        conn.commit()
    conn.close()

init_db()

class ItemCreate(BaseModel):
    id: str
    category: str
    title: str
    image: str
    highlight: str
    fact1: str
    fact2: str
    fact3: str
    fact4: str
    summary: str
    action_text: str = "확인하기 ↗"
    action_color: str = "bg-rose-600"
    source: str = "웹 정보"
    tags: str = ""

@app.get("/")
def read_root():
    return {"status": "online", "message": "Visual Search API is running"}

@app.get("/api/search")
def search_items(
    q: Optional[str] = Query("", description="검색어"),
    category: Optional[str] = Query("all", description="카테고리")
):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = q.strip()
    if query:
        pattern = f"%{query}%"
        if category and category != "all":
            sql = """
            SELECT * FROM items 
            WHERE category = ? AND (
                title LIKE ? OR highlight LIKE ? OR summary LIKE ? OR tags LIKE ? OR fact1 LIKE ? OR fact2 LIKE ?
            )
            """
            cur.execute(sql, (category, pattern, pattern, pattern, pattern, pattern, pattern))
        else:
            sql = """
            SELECT * FROM items 
            WHERE title LIKE ? OR highlight LIKE ? OR summary LIKE ? OR tags LIKE ? OR fact1 LIKE ? OR fact2 LIKE ?
            """
            cur.execute(sql, (pattern, pattern, pattern, pattern, pattern, pattern))
    else:
        if category and category != "all":
            cur.execute("SELECT * FROM items WHERE category = ?", (category,))
        else:
            cur.execute("SELECT * FROM items")

    rows = cur.fetchall()
    results = [dict(row) for row in rows]
    conn.close()

    return {
        "count": len(results),
        "query": query,
        "category": category,
        "results": results
    }

@app.post("/api/items")
def add_item(item: ItemCreate):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        item.id, item.category, item.title, item.image, item.highlight,
        item.fact1, item.fact2, item.fact3, item.fact4, item.summary,
        item.action_text, item.action_color, item.source, item.tags
    ))
    conn.commit()
    conn.close()
    return {"status": "success", "id": item.id}