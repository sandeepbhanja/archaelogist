from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from agents import ReActLoop


app = FastAPI()

@app.get("/start")
async def agentStart(request:Request):
    data = await request.json()
    print(data)
    query = data["query"]
    ReActLoop(query)