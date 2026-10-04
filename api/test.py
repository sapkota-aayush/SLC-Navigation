from lib.vercel_api import ApiHandler


class handler(ApiHandler):
    def do_GET(self):
        self._json(200, {"message": "Python serverless function is working!"})
