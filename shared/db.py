"""대화 영속 저장 (SQLite) — 모든 버전(v1~v4)이 공유하는 DB 레이어

메시지를 messages 테이블에 (session_id, role, content)로 저장하고,
session_id 로 지난 대화를 불러온다. 메모리 딕셔너리와 달리 서버를 꺼도 보존.
"""

import os
import sqlite3

# DB 파일 위치: shared/data/chat.db (실행 폴더와 무관하게 이 파일 기준으로 고정)
DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "chat.db")


def _connect():
    """매 작업마다 새 연결을 열고 닫음 (스레드 안전, 단순)"""
    return sqlite3.connect(DB_PATH)


def init_db():
    """messages 테이블이 없으면 생성 (서버 시작 시 1회 호출)"""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_message(session_id: str, role: str, content: str):
    """메시지 한 줄을 DB에 저장"""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


def get_history(session_id: str) -> list[dict]:
    """해당 session_id 의 대화 전체를 시간순으로 반환 (Claude messages 형식)"""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    return [{"role": role, "content": content} for role, content in rows]
