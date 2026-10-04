from lib.vercel_api import ApiHandler, get_nav


class handler(ApiHandler):
    def do_GET(self):
        nav = get_nav()
        self._json(200, {"status": "ok", "ai_enabled": nav.ai_enabled})
