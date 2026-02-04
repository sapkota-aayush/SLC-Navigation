"""
Flask API server for navigation system
Connects Python pathfinding to web frontend
"""

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import requests
from io import BytesIO
from PIL import Image
from ai_navigation import AINavigationSystem

app = Flask(__name__)
# Allow all origins for CORS (including custom domain slcnavigation.aayussh.com)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

# Disable caching for API responses
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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
    search_type = data.get('type', 'destination')
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    try:
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

@app.route('/api/image/webp', methods=['GET'])
def convert_to_webp():
    """
    Convert Supabase image to WebP format on-the-fly
    Query param: url - the Supabase image URL
    Optional param: quality - WebP quality (1-100, default: 80)
    Optional param: max_width - max width in pixels (default: 1200)
    """
    image_url = request.args.get('url')
    quality = int(request.args.get('quality', 80))
    max_width = int(request.args.get('max_width', 1200))
    
    if not image_url:
        return jsonify({'success': False, 'error': 'URL parameter required'}), 400
    
    try:
        # Fetch image from Supabase
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open image with Pillow
        img = Image.open(BytesIO(response.content))
        
        # Convert RGBA to RGB if necessary (WebP supports both, but RGB is smaller)
        if img.mode == 'RGBA':
            # Create white background
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = rgb_img
        elif img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Resize if larger than max_width (maintain aspect ratio)
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to WebP
        webp_buffer = BytesIO()
        img.save(webp_buffer, format='WEBP', quality=quality, method=6)
        webp_buffer.seek(0)
        
        # Return WebP image with proper caching
        return Response(
            webp_buffer.getvalue(),
            mimetype='image/webp',
            headers={
                'Cache-Control': 'public, max-age=31536000',  # Cache for 1 year
                'Content-Type': 'image/webp'
            }
        )
        
    except requests.RequestException as e:
        return jsonify({'success': False, 'error': f'Failed to fetch image: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to convert image: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    # Disable Flask's automatic dotenv loading to avoid permission errors
    import flask.cli
    flask.cli.load_dotenv = lambda *args, **kwargs: None
    app.run(debug=False, host='0.0.0.0', port=port)




