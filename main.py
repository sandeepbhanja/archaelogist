from fastapi import FastAPI
from contextlib import asynccontextmanager

from agents import ReActLoop


app = FastAPI()

@app.get("/start")
async def agentStart():
    ReActLoop()