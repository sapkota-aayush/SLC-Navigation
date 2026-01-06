"""
Vercel serverless function for AI search
"""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_navigation import AINavigationSystem

nav_system = None

def handler(req):
    global nav_system
    if nav_system is None:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'navigation_data.json')
        nav_system = AINavigationSystem(json_path)
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    }
    
    if req.method == 'OPTIONS':
        return json.dumps({}), {'statusCode': 200, 'headers': headers}
    
    try:
        body = json.loads(req.body) if req.body else {}
        query = body.get('query', '').strip()
        search_type = body.get('type', 'destination')
        
        if not query:
            return json.dumps({'success': False, 'error': 'Search query required'}), {
                'statusCode': 400,
                'headers': headers
            }
        
        node_id = None
        if query.isdigit():
            node_id = nav_system.find_node_by_room(query)
        
        if not node_id:
            node_id = nav_system.find_node_by_name(query)
        
        if not node_id:
            node_id = nav_system._match_location_with_ai(query, search_type)
        
        if node_id:
            node = next((n for n in nav_system.nodes if n['id'] == node_id), None)
            if node:
                return json.dumps({
                    'success': True,
                    'node_id': node_id,
                    'name': node['name'],
                    'type': node.get('type', ''),
                    'matched_via': 'direct' if node_id else 'ai'
                }), {
                    'statusCode': 200,
                    'headers': headers
                }
        
        return json.dumps({
            'success': False,
            'error': f'Could not find location matching "{query}". Try: Room numbers, Library, Cafeteria, etc.'
        }), {
            'statusCode': 404,
            'headers': headers
        }
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}), {
            'statusCode': 500,
            'headers': headers
        }

