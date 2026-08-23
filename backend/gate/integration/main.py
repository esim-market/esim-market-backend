import os

from backend.gate.integration.api_app_base import ApiAppBase

app = ApiAppBase(os.getenv("ROOT_PATH", "")).create_app()
