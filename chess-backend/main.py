import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chess import llm_move, llm_chat
from routes.rpg import render_level, perform_action

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app.include_router(llm_move.router)
app.include_router(llm_chat.router)












