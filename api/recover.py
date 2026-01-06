"""
Vercel serverless function for recovery
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
        landmark = body.get('landmark', '')
        
        if not landmark:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'success': False, 'error': 'Landmark required'})
            }
        
        result = nav_system.recover_from_landmark(landmark)
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'success': False, 'error': str(e)})
        }

