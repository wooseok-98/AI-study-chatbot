"""FastAPI 앱 진입점 + uvicorn 런처"""

import os
import sys

# 상위 폴더(chatbot_project) = 프로젝트 루트
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)  # 바깥의 shared 패키지를 import 가능하게

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

load_dotenv(os.path.join(BASE_DIR, ".env"))  # 루트의 .env 를 명시적으로 로드

from shared import db
from app.routers import health_router, chat_router

db.init_db()  # messages 테이블 준비 (없으면 생성)

app = FastAPI(title="AI 학습 도우미 챗봇 - v4 (LangGraph 에이전트)")

app.include_router(health_router.router)
app.include_router(chat_router.router)

# 정적 파일(css/js) 서빙 + 루트에서 채팅 화면 제공
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
