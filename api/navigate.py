"""
Vercel serverless function for navigation
"""
import json
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_navigation import AINavigationSystem

# Initialize navigation system (loaded once per container)
nav_system = None

def handler(req):
    """Vercel serverless function handler"""
    global nav_system
    
    # Lazy load navigation system
    if nav_system is None:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'navigation_data.json')
        nav_system = AINavigationSystem(json_path)
    
    # Handle CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    }
    
    # Handle preflight
    if req.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        body = json.loads(req.body) if req.body else {}
        start_location = body.get('start_location', '')
        destination = body.get('destination', '')
        use_ai = body.get('use_ai', True)
        
        if not start_location:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'success': False, 'error': 'Start location required'})
            }
        
        if not destination:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'success': False, 'error': 'Destination required'})
            }
        
        result = nav_system.navigate_from_to(start_location, destination, use_ai=use_ai)
        
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

