from lib.vercel_api import ApiHandler, get_nav


class handler(ApiHandler):
    def do_POST(self):
        try:
            body = self.read_json()
            query = (body.get("query") or "").strip()
            search_type = body.get("type", "destination")
            if not query:
                self._json(400, {"success": False, "error": "Search query required"})
                return

            nav = get_nav()
            node_id = None
            matched_via = None
            if query.isdigit():
                node_id = nav.find_node_by_room(query)
                if node_id:
                    matched_via = "direct"
            if not node_id:
                node_id = nav.find_node_by_name(query)
                if node_id:
                    matched_via = "direct"
            if not node_id:
                node_id = nav._match_location_with_ai(query, search_type)
                if node_id:
                    matched_via = "ai"

            if node_id:
                node = next((n for n in nav.nodes if n["id"] == node_id), None)
                if node:
                    self._json(
                        200,
                        {
                            "success": True,
                            "node_id": node_id,
                            "name": node["name"],
                            "type": node.get("type", ""),
                            "matched_via": matched_via,
                        },
                    )
                    return

            self._json(
                404,
                {
                    "success": False,
                    "error": f'Could not find location matching "{query}". Try: Room numbers, Library, Cafeteria, etc.',
                },
            )
        except Exception as e:
            self._json(500, {"success": False, "error": str(e)})
