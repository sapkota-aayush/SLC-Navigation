from lib.vercel_api import ApiHandler, get_nav


class handler(ApiHandler):
    def do_POST(self):
        try:
            body = self.read_json()
            start_location = body.get("start_location", "")
            destination = body.get("destination", "")
            use_ai = body.get("use_ai", True)

            if not start_location:
                self._json(400, {"success": False, "error": "Start location required"})
                return
            if not destination:
                self._json(400, {"success": False, "error": "Destination required"})
                return

            result = get_nav().navigate_from_to(
                start_location, destination, use_ai=use_ai
            )
            self._json(200, result)
        except Exception as e:
            self._json(500, {"success": False, "error": str(e)})
