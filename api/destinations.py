"""
Vercel serverless function for getting destinations
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
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    }
    
    if req.method == 'OPTIONS':
        return json.dumps({}), {'statusCode': 200, 'headers': headers}
    
    try:
        destinations = nav_system.get_available_destinations()
        return json.dumps({'success': True, 'destinations': destinations}), {
            'statusCode': 200,
            'headers': headers
        }
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}), {
            'statusCode': 500,
            'headers': headers
        }

