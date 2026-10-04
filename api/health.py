import os

from ai_navigation import OPENAI_AVAILABLE
from lib.vercel_api import ApiHandler, get_nav


class handler(ApiHandler):
    def do_GET(self):
        nav = get_nav()
        payload = {"status": "ok", "ai_enabled": nav.ai_enabled}
        if not nav.ai_enabled:
            payload["openai_installed"] = OPENAI_AVAILABLE
            payload["key_configured"] = bool(os.getenv("OPENAI_API_KEY"))
        self._json(200, payload)
