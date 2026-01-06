"""
Flask API server for navigation system
Connects Python pathfinding to web frontend
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
from ai_navigation import AINavigationSystem

app = Flask(__name__, static_folder='images', static_url_path='/static')
CORS(app)  # Allow React frontend to access API

# Disable caching for API responses
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Images are now served via Flask's static_folder - no custom route needed!

# Initialize navigation system
nav_system = AINavigationSystem('navigation_data.json')

@app.route('/api/navigate', methods=['POST'])
def navigate():
    """Navigate from start location to destination"""
    data = request.json
    start_location = data.get('start_location', '')
    destination = data.get('destination', '')
    use_ai = data.get('use_ai', True)
    
    if not start_location:
        return jsonify({'success': False, 'error': 'Start location required'}), 400
    if not destination:
        return jsonify({'success': False, 'error': 'Destination required'}), 400
    
    try:
        result = nav_system.navigate_from_to(start_location, destination, use_ai=use_ai)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/destinations', methods=['GET'])
def get_destinations():
    """Get all available destinations"""
    try:
        destinations = nav_system.get_available_destinations()
        return jsonify({'success': True, 'destinations': destinations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recover', methods=['POST'])
def recover():
    """Recover navigation from a landmark"""
    data = request.json
    landmark = data.get('landmark', '')
    
    if not landmark:
        return jsonify({'success': False, 'error': 'Landmark required'}), 400
    
    try:
        result = nav_system.recover_from_landmark(landmark)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def ai_search():
    """AI-based search - interpret natural language queries"""
    data = request.json
    query = data.get('query', '').strip()
    search_type = data.get('type', 'destination')  # 'start' or 'destination'
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    try:
        # First try direct lookup
        node_id = None
        
        # Try room number first
        if query.isdigit():
            node_id = nav_system.find_node_by_room(query)
        
        # Try name lookup
        if not node_id:
            node_id = nav_system.find_node_by_name(query)
        
        # If direct lookup fails, use AI
        if not node_id:
            node_id = nav_system._match_location_with_ai(query, search_type)
        
        if node_id:
            # Get node details
            node = next((n for n in nav_system.nodes if n['id'] == node_id), None)
            if node:
                return jsonify({
                    'success': True,
                    'node_id': node_id,
                    'name': node['name'],
                    'type': node.get('type', ''),
                    'matched_via': 'direct' if node_id else 'ai'
                })
        
        return jsonify({
            'success': False,
            'error': f'Could not find location matching "{query}". Try: Room numbers, Library, Cafeteria, etc.'
        }), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'ai_enabled': nav_system.ai_enabled
    })

if __name__ == '__main__':
    print("🚀 Starting Navigation API Server...")
    print("📍 API available at http://localhost:5001")
    print("🤖 AI Features:", "Enabled" if nav_system.ai_enabled else "Disabled")
    app.run(debug=True, port=5001, host='0.0.0.0')

