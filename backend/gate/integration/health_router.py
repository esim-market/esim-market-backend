from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "live"}


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    mongodb_client = getattr(request.app.state, "mongodb_client", None)
    redis_repository = getattr(request.app.state, "redis_repository", None)

    if mongodb_client is None or redis_repository is None:
        return JSONResponse(status_code=503, content={"status": "not_ready"})

    try:
        await mongodb_client.admin.command("ping")
        await redis_repository.ping()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return JSONResponse(status_code=200, content={"status": "ready"})
