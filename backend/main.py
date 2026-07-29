from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import automations, chat, memory, profile, tasks, ws_tasks
from db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Jarvis API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(profile.router)
app.include_router(tasks.router)
app.include_router(ws_tasks.router)
app.include_router(automations.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
