"""
AI-Powered Image Recognition for Navigation Recovery
Uses OpenAI Vision API to match user photos with navigation landmarks
"""

import os
import base64
import json
from typing import Dict, Optional, List
from pathfinding import NavigationSystem

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Run: pip install openai")


class AINavigationSystem(NavigationSystem):
    """Extended navigation system with AI image recognition"""
    
    def __init__(self, json_file_path: str):
        super().__init__(json_file_path)
        
        # Load API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # Try loading from .env file
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv('OPENAI_API_KEY')
            except (ImportError, PermissionError, Exception):
                # If .env file can't be read (permission issues, etc), continue without it
                pass
        
        if api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=api_key)
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False
            if not OPENAI_AVAILABLE:
                print("Warning: OpenAI package not installed. AI features disabled.")
            else:
                print("Warning: OPENAI_API_KEY not found. AI features disabled.")
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode image to base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None
    
    def _get_image_mime_type(self, image_path: str) -> str:
        """Determine MIME type from file extension"""
        ext = image_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        return mime_types.get(ext, 'image/jpeg')
    
    def identify_location_from_photo(self, user_photo_path: str) -> Dict:
        """
        Use AI to identify which navigation location matches the user's photo
        
        Args:
            user_photo_path: Path to user's photo
        
        Returns:
            Dictionary with identified location or error
        """
        if not self.ai_enabled:
            return {
                'success': False,
                'error': 'AI features not enabled. Check API key.'
            }
        
        if not os.path.exists(user_photo_path):
            return {
                'success': False,
                'error': f'Photo not found: {user_photo_path}'
            }
        
        # Encode user photo
        user_image_base64 = self._encode_image(user_photo_path)
        if not user_image_base64:
            return {
                'success': False,
                'error': 'Failed to encode user photo'
            }
        
        # Prepare all navigation photos for comparison
        navigation_photos = []
        for node in self.nodes:
            photo_path = node['photo']
            if os.path.exists(photo_path):
                nav_image_base64 = self._encode_image(photo_path)
                if nav_image_base64:
                    navigation_photos.append({
                        'node': node,
                        'image': nav_image_base64,
                        'mime_type': self._get_image_mime_type(photo_path)
                    })
        
        if not navigation_photos:
            return {
                'success': False,
                'error': 'No navigation photos found for comparison'
            }
        
        # Create prompt for OpenAI
        location_names = [p['node']['name'] for p in navigation_photos]
        prompt = f"""You are a navigation assistant. Compare this user's photo with the following locations:
{', '.join(location_names)}

Identify which location the user is currently at. Consider:
- Architectural features (stairs, reception desks, windows, layout)
- Signage and text visible
- Overall structure and design
- Furniture and fixtures

Respond with ONLY the exact location name that best matches, or "UNKNOWN" if none match well."""

        try:
            # Prepare messages with user photo and navigation photos
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{self._get_image_mime_type(user_photo_path)};base64,{user_image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Add navigation photos for comparison
            for nav_photo in navigation_photos:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Reference photo for: {nav_photo['node']['name']}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{nav_photo['mime_type']};base64,{nav_photo['image']}"
                            }
                        }
                    ]
                })
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4-vision-preview"
                messages=messages,
                max_tokens=100
            )
            
            identified_location = response.choices[0].message.content.strip()
            
            # Find matching node
            for nav_photo in navigation_photos:
                if nav_photo['node']['name'].lower() in identified_location.lower():
                    return {
                        'success': True,
                        'location': nav_photo['node'],
                        'confidence': identified_location,
                        'identified_name': identified_location
                    }
            
            return {
                'success': False,
                'error': f'Location not recognized. AI response: {identified_location}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI recognition failed: {str(e)}'
            }
    
    def recover_from_photo(self, user_photo_path: str) -> Dict:
        """
        Recovery function - identify location from photo and reset navigation
        
        Args:
            user_photo_path: Path to user's photo
        
        Returns:
            Dictionary with recovery result
        """
        # Identify location
        identification = self.identify_location_from_photo(user_photo_path)
        
        if not identification['success']:
            return identification
        
        # Recover from identified landmark
        location_name = identification['location']['name']
        recovery = self.recover_from_landmark(location_name)
        
        if recovery['success']:
            return {
                'success': True,
                'identified_location': identification['location'],
                'new_start': recovery['new_start'],
                'message': f'Navigation reset from {location_name}'
            }
        else:
            return {
                'success': False,
                'error': f'Identified location but recovery failed: {recovery.get("error")}'
            }
    
    def _match_location_with_ai(self, user_input: str, location_type: str = "location") -> Optional[str]:
        """
        Use AI to match user input to available locations
        
        Args:
            user_input: What the user typed (e.g., "st larry pub", "cafeteria")
            location_type: "start" or "destination" for better context
        
        Returns:
            Node ID if matched, None otherwise
        """
        if not self.ai_enabled:
            return None
        
        # Get all available locations
        available_locations = []
        for node in self.nodes:
            available_locations.append({
                'name': node['name'],
                'id': node['id'],
                'rooms': node.get('rooms', []),
                'type': node.get('type', '')
            })
        
        # Create location list for AI
        location_list = '\n'.join([
            f"- {loc['name']} (ID: {loc['id']}, Rooms: {', '.join(loc['rooms']) if loc['rooms'] else 'none'})"
            for loc in available_locations
        ])
        
        prompt = f"""You are a navigation assistant. The user said: "{user_input}"

Available locations in the building:
{location_list}

Your task: Match the user's input to the correct location from the list above.
Consider:
- Typos and variations (e.g., "st larry pub" = "St. Larry's Pub")
- Abbreviations (e.g., "cafe" = "Cafeteria")
- Partial matches (e.g., "fitness" = "Fitness Center")
- Room numbers if mentioned
- Common synonyms
- Printers are inside the Library: if the user asks for "printers", "printer", "where to print", or "I need to print", use location ID: library.

Respond with ONLY the exact location ID from the list above (e.g., "st_larrys_pub", "cafeteria", "fitness_center", "library").
If no good match, respond with "NOT_FOUND"."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful navigation assistant that matches user input to location names. Always respond with the exact location ID or NOT_FOUND."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            matched_id = response.choices[0].message.content.strip()
            
            if matched_id == "NOT_FOUND" or not matched_id:
                return None
            
            # Verify the ID exists
            for node in self.nodes:
                if node['id'] == matched_id:
                    return matched_id
            
            return None
        except Exception as e:
            print(f"AI location matching error: {e}")
            return None
    
    def navigate_from_to(self, start_location: str, destination: str, use_ai: bool = True) -> Dict:
        """
        Navigate from a custom start location to destination with AI understanding
        
        Args:
            start_location: Natural language description of where user is (e.g., "I'm at the library", "Main Entrance")
            destination: Natural language description of where user wants to go (e.g., "Room 101", "I need to go to cafeteria")
            use_ai: If True, use AI to understand natural language
        
        Returns:
            Dictionary with path and AI-generated instructions
        """
        # Try direct lookup first (fast, reliable)
        start_id = self.find_node_by_room(start_location) or self.find_node_by_name(start_location)
        
        # If not found and AI is enabled, use AI to match
        if not start_id and use_ai and self.ai_enabled:
            start_id = self._match_location_with_ai(start_location, "start")
        
        if not start_id:
            # Get suggestions
            suggestions = [node['name'] for node in self.nodes[:5]]
            return {
                'success': False,
                'error': f'Could not find start location: "{start_location}". Try: {", ".join(suggestions)}, etc.'
            }
        
        # Try direct lookup first for destination
        destination_id = self.find_node_by_room(destination) or self.find_node_by_name(destination)
        
        # If not found and AI is enabled, use AI to match
        if not destination_id and use_ai and self.ai_enabled:
            destination_id = self._match_location_with_ai(destination, "destination")
        
        if not destination_id:
            # Get suggestions
            suggestions = [node['name'] for node in self.nodes[:5]]
            return {
                'success': False,
                'error': f'Could not find destination: "{destination}". Try: {", ".join(suggestions)}, etc.'
            }
        
        if start_id == destination_id:
            return {
                'success': False,
                'error': 'You are already at your destination!'
            }
        
        # Find path using BFS
        path = self.find_path_bfs(start_id, destination_id)
        
        if not path:
            return {
                'success': False,
                'error': f'No path found from {start_location} to {destination}'
            }
        
        # Get full node details for path
        path_nodes = []
        for node_id in path:
            node = next((n for n in self.nodes if n['id'] == node_id), None)
            if node:
                path_nodes.append(node)
        
        start_node = next((n for n in self.nodes if n['id'] == start_id), None)
        dest_node = next((n for n in self.nodes if n['id'] == destination_id), None)
        
        result = {
            'success': True,
            'path': path,
            'path_nodes': path_nodes,
            'photos': [node['photo'] for node in path_nodes],
            'start': start_node,
            'destination': dest_node
        }
        
        # Generate AI instructions if enabled
        if use_ai and self.ai_enabled:
            ai_instructions = self._generate_ai_instructions(path_nodes, start_node, dest_node)
            result['ai_instructions'] = ai_instructions
        
        return result
    
    def _understand_location_with_ai(self, location_text: str, is_start: bool = False) -> Optional[str]:
        """
        Use AI to understand natural language location descriptions
        
        Args:
            location_text: Natural language description
            is_start: True if this is the start location
        
        Returns:
            Node ID if found, None otherwise
        """
        if not self.ai_enabled:
            return None
        
        # First try direct lookup
        node_id = self.find_node_by_room(location_text) or self.find_node_by_name(location_text)
        if node_id:
            return node_id
        
        # Get all available locations
        available_locations = []
        for node in self.nodes:
            available_locations.append({
                'name': node['name'],
                'id': node['id'],
                'rooms': node.get('rooms', []),
                'type': node.get('type', '')
            })
        
        # Create prompt for AI
        location_list = '\n'.join([f"- {loc['name']} (rooms: {', '.join(loc['rooms']) if loc['rooms'] else 'none'})" 
                                  for loc in available_locations])
        
        prompt = f"""You are a navigation assistant. The user said: "{location_text}"

Available locations in the building:
{location_list}

Determine which location the user is referring to. Consider:
- Room numbers mentioned (e.g., "101", "room 102")
- Location names (e.g., "library", "cafeteria", "main entrance")
- Natural language descriptions (e.g., "I'm at the stairs", "where the food is")
- Partial matches and synonyms
- Printers are inside the Library: if the user asks for printers, printer, or where to print, respond with "Library".

Respond with ONLY the exact location name from the list above, or "NOT_FOUND" if none match."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful navigation assistant. Be precise and match locations exactly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Find matching node
            for loc in available_locations:
                if loc['name'].lower() in ai_response.lower() or ai_response.lower() in loc['name'].lower():
                    return loc['id']
            
            return None
            
        except Exception as e:
            print(f"AI location understanding error: {e}")
            return None
    
    def _generate_ai_instructions(self, path_nodes: List[Dict], start_node: Dict, dest_node: Dict) -> str:
        """Generate simple, concise AI instructions for the path"""
        # Build path with descriptions and floor information
        path_steps = []
        for i, node in enumerate(path_nodes):
            if i < len(path_nodes) - 1:
                next_node = path_nodes[i + 1]
                current_floor = node.get('floor', 1)
                next_floor = next_node.get('floor', 1)
                
                # Determine floor direction
                floor_info = ""
                if current_floor < next_floor:
                    floor_info = f" [GOING UP from floor {current_floor} to floor {next_floor}]"
                elif current_floor > next_floor:
                    floor_info = f" [GOING DOWN from floor {current_floor} to floor {next_floor}]"
                else:
                    floor_info = f" [Same floor {current_floor}]"
                
                step_desc = f"{node['name']} (Floor {current_floor}) -> {next_node['name']} (Floor {next_floor}){floor_info}: {next_node.get('description', '')}"
                path_steps.append(step_desc)
        
        path_description = "\n".join(path_steps)
        start_floor = start_node.get('floor', 1)
        dest_floor = dest_node.get('floor', 1)
        
        instructions_prompt = f"""You are a navigation assistant. Provide descriptive directions that tell users what they will SEE, not just generic "go straight" commands.

Path: {start_node['name']} (Floor {start_floor}) to {dest_node['name']} (Floor {dest_floor})

Step descriptions with floor information:
{path_description}

CRITICAL RULES:
- NEVER use technical node names like "Hallway 1", "Hallway 3", "Hallway 4" - users don't know what these mean
- DESCRIBE WHAT THEY'LL SEE: "You'll see rooms on your right side", "Look for the green sign above the doors", "You'll see a long hallway with doors on both sides"
- Instead of "go straight", say: "Keep walking forward", "Continue down the hallway", "Walk straight ahead through this area"
- Instead of generic directions, describe landmarks: "Pass the BookStore on your right", "Walk past the Cafeteria", "You'll see the Library ahead"
- If the destination is the Library (e.g. user asked for printers): mention that the printers are inside the Library so they know they've arrived at the right place
- For hallways with rooms: "You'll see rooms numbered [X-Y] on your right/left side, keep moving forward"
- For entrances: "You'll see this entrance/hallway ahead, walk through it"
- Pay attention to floor numbers! If going from floor 0 to floor 1, say "go upstairs" or "go up to floor 1"
- If going from floor 1 to floor 0, say "go downstairs" or "go down to basement"
- If locations are on the same floor, don't mention going up or down
- Keep it to 2-3 sentences maximum
- Be clear and descriptive - tell them what visual cues to look for
- Write as a simple paragraph, not a list

Examples:
- BAD: "Go straight"
- GOOD: "Keep walking forward through the hallway. You'll see rooms on your right side, continue moving ahead"
- BAD: "Turn left after Hallway 3"
- GOOD: "At the next opening, turn left. You'll see a hallway with doors on both sides"
- GOOD: "Walk past the Cafeteria and continue straight. You'll see rooms numbered 11010-11050 on your right side - keep moving forward"
- GOOD: "You'll see this entrance ahead with glass doors and a green sign above. Walk through it and continue down the hallway"

Provide the directions now (describe what they'll see, use natural language, no technical names):"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful indoor navigation assistant. Provide simple, clear directions in 2-3 sentences as a paragraph."},
                    {"role": "user", "content": instructions_prompt}
                ],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating instructions: {str(e)}"
    
    def get_navigation_instructions(self, destination: str, use_ai: bool = True) -> Dict:
        """
        Get AI-generated navigation instructions for the path
        
        Args:
            destination: Room number or location name
            use_ai: If True, generate AI instructions
        
        Returns:
            Dictionary with path and AI-generated instructions
        """
        # Get path first
        nav_result = self.navigate(destination)
        
        if not nav_result['success']:
            return nav_result
        
        if not use_ai or not self.ai_enabled:
            return nav_result
        
        # Generate AI instructions
        path_description = " -> ".join([node['name'] for node in nav_result['path_nodes']])
        
        instructions_prompt = f"""You are a navigation assistant. Provide clear, step-by-step directions for this path:
{path_description}

For each step, provide:
1. Where to go (left, right, straight, up stairs, etc.)
2. What to look for (landmarks, signs, features)
3. Brief description of what they'll see

Make it friendly and easy to follow. Format as a numbered list."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful indoor navigation assistant."},
                    {"role": "user", "content": instructions_prompt}
                ],
                max_tokens=300
            )
            
            instructions = response.choices[0].message.content.strip()
            
            nav_result['ai_instructions'] = instructions
            return nav_result
            
        except Exception as e:
            nav_result['ai_instructions'] = None
            nav_result['ai_error'] = str(e)
            return nav_result


if __name__ == "__main__":
    # Test AI features
    print("=== AI Navigation System Test ===\n")
    
    ai_nav = AINavigationSystem('navigation_data.json')
    
    if ai_nav.ai_enabled:
        print("✓ AI features enabled\n")
        
        # Test navigation with AI instructions
        print("Test: Get navigation instructions to Room 101")
        result = ai_nav.get_navigation_instructions("101")
        
        if result['success']:
            print(f"\nPath: {' -> '.join([n['name'] for n in result['path_nodes']])}")
            if 'ai_instructions' in result and result['ai_instructions']:
                print(f"\nAI Instructions:\n{result['ai_instructions']}")
        else:
            print(f"Error: {result['error']}")
    else:
        print("✗ AI features not available")
        print("Make sure OPENAI_API_KEY is set in .env file")

