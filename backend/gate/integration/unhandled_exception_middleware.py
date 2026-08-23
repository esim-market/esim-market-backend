from __future__ import annotations

from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from backend.common.logging import get_logger

logger = get_logger(__name__)


class UnhandledExceptionMiddleware:
    """Hide unexpected exception details behind a stable client error contract."""

    http_status_code = 520
    application_error_code = "ESIM-UNHANDLED-001"
    client_message = "An unexpected error occurred."

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def tracked_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, tracked_send)
        except Exception:
            request_id = uuid4().hex
            logger.exception(
                "Unhandled request exception [request_id=%s method=%s path=%s]",
                request_id,
                scope.get("method", "UNKNOWN"),
                scope.get("path", ""),
            )
            if response_started:
                raise

            response = JSONResponse(
                status_code=self.http_status_code,
                content={
                    "error": {
                        "code": self.application_error_code,
                        "message": self.client_message,
                        "request_id": request_id,
                    }
                },
                headers={"X-Request-ID": request_id},
            )
            await response(scope, receive, send)
