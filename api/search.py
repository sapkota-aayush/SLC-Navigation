"""
Vercel serverless function for AI search
"""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_navigation import AINavigationSystem

nav_system = None

def handler(request):
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
    
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        body_str = request.body if hasattr(request, 'body') else ''
        if isinstance(body_str, bytes):
            body_str = body_str.decode('utf-8')
        body = json.loads(body_str) if body_str else {}
        query = body.get('query', '').strip()
        search_type = body.get('type', 'destination')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'success': False, 'error': 'Search query required'})
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
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'node_id': node_id,
                        'name': node['name'],
                        'type': node.get('type', ''),
                        'matched_via': 'direct' if node_id else 'ai'
                    })
                }
        
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': f'Could not find location matching "{query}". Try: Room numbers, Library, Cafeteria, etc.'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'error': str(e)})
        }

