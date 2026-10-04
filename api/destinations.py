from lib.vercel_api import ApiHandler, get_nav


class handler(ApiHandler):
    def do_GET(self):
        try:
            destinations = get_nav().get_available_destinations()
            self._json(200, {"success": True, "destinations": destinations})
        except Exception as e:
            self._json(500, {"success": False, "error": str(e)})
