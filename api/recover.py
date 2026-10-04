from lib.vercel_api import ApiHandler, get_nav


class handler(ApiHandler):
    def do_POST(self):
        try:
            body = self.read_json()
            landmark = body.get("landmark", "")
            if not landmark:
                self._json(400, {"success": False, "error": "Landmark required"})
                return
            result = get_nav().recover_from_landmark(landmark)
            self._json(200, result)
        except Exception as e:
            self._json(500, {"success": False, "error": str(e)})
