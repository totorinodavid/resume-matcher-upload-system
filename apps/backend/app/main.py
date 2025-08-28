import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import json
from typing import AsyncIterator
# All CORS, Auth (HTTPBearer + Clerk JWT), and Stripe webhook routing are configured in create_app().
from .base import create_app

app = create_app()

# Lightweight OpenAI pass-through streaming endpoint to harden timeouts on Render
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

_client = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=60.0),
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
)

@app.post("/match-stream", include_in_schema=False)
async def match_stream(payload: dict) -> StreamingResponse:
    prompt = payload.get("prompt", "")
    if not OPENAI_API_KEY:
        async def _err() -> AsyncIterator[bytes]:
            yield b"data: {\"error\":\"OPENAI_API_KEY not set\"}\n\n"
        return StreamingResponse(_err(), media_type="text/event-stream")

    async def gen() -> AsyncIterator[str]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        body = {
            "model": "gpt-4o-mini",
            "stream": True,
            "temperature": 0.2,
            "max_tokens": 800,
            "messages": [
                {"role": "system", "content": "Du bist ein präziser CV-ATS-Matcher."},
                {"role": "user", "content": prompt},
            ],
        }
        async with _client.stream("POST", url, headers=headers, json=body) as r:
            async for line in r.aiter_lines():
                if not line:
                    await asyncio.sleep(0)
                    continue
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    yield f"data: {chunk}\n\n"
                await asyncio.sleep(0)

    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
