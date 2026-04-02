import asyncio, json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.pipeline_manager import subscribe, unsubscribe, log_buffer

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/stream")
async def stream_logs():
    """SSE endpoint — streams live pipeline logs to frontend."""
    async def gen():
        # send buffered history so the UI isn't blank on connect
        for msg in list(log_buffer):
            yield f"data: {json.dumps({'log': msg})}\n\n"

        q = subscribe()
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=25)
                    yield f"data: {json.dumps({'log': msg})}\n\n"
                except asyncio.TimeoutError:
                    yield 'data: {"ping":true}\n\n'   # keepalive
        except asyncio.CancelledError:
            pass
        finally:
            unsubscribe(q)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )