from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.staticfiles import StaticFiles

from backend.common.env.redis_env_settings import RedisEnvSettings
from backend.common.env.settings import MongoSettings
from backend.common.logging import configure_logging, get_logger
from backend.common.mongodb_lifecycle_mixin import MongoDbLifecycleMixin
from backend.common.redis_lifecycle_mixin import RedisLifecycleMixin
from .health_router import router as health_router
from .unhandled_exception_middleware import UnhandledExceptionMiddleware

logger = get_logger(__name__)


class ApiAppBase(MongoDbLifecycleMixin, RedisLifecycleMixin):
    def __init__(self, root_path: str = ""):
        self.root_path = root_path

    def create_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            configure_logging()
            try:
                await self.open_mongodb(MongoSettings())
            except Exception:
                logger.exception("MongoDB is unavailable during API startup")
            try:
                await self.open_redis(RedisEnvSettings())
            except Exception:
                logger.exception("Redis is unavailable during API startup")
            app.state.mongodb_client = getattr(self, "mongodb_client", None)
            app.state.redis_connection = getattr(self, "redis_connection", None)
            app.state.redis_repository_factory = getattr(self, "redis_repository_factory", None)
            app.state.redis_repository = getattr(self, "redis_repository", None)
            try:
                yield
            finally:
                await self.close_redis()
                await self.close_mongodb()

        app = FastAPI(root_path=self.root_path, docs_url=None, redoc_url=None, lifespan=lifespan)
        app.add_middleware(UnhandledExceptionMiddleware)
        static_dir = Path(__file__).resolve().parents[2] / "static"
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        app.include_router(health_router)

        @app.get("/docs", include_in_schema=False)
        async def docs():
            return get_swagger_ui_html(openapi_url=f"{self.root_path}/openapi.json", title="eSIM Market API", oauth2_redirect_url=f"{self.root_path}/docs/oauth2-redirect", swagger_js_url=f"{self.root_path}/static/swagger-ui-bundle.js", swagger_css_url=f"{self.root_path}/static/swagger-ui.css")

        @app.get("/docs/oauth2-redirect", include_in_schema=False)
        async def oauth2_redirect():
            return get_swagger_ui_oauth2_redirect_html()

        @app.get("/redoc", include_in_schema=False)
        async def redoc():
            return get_redoc_html(openapi_url=f"{self.root_path}/openapi.json", title="eSIM Market API", redoc_js_url=f"{self.root_path}/static/redoc.standalone.js")

        return app
