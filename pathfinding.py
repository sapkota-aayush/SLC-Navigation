"""
Navigation Pathfinding System
Implements BFS (Breadth-First Search) and DFS (Depth-First Search)
"""

import json
from collections import deque
from typing import List, Dict, Optional, Tuple


class NavigationSystem:
    def __init__(self, json_file_path: str):
        """Initialize navigation system from JSON file"""
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        self.nodes = data['nodes']
        self.start_node = data['start_node']
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Dict[str, List[str]]:
        """Build adjacency list graph from nodes (bidirectional connections)"""
        graph = {}
        
        # Initialize all nodes
        for node in self.nodes:
            graph[node['id']] = []
        
        # Add connections (bidirectional)
        for node in self.nodes:
            for connected_id in node['connects_to']:
                if connected_id not in graph[node['id']]:
                    graph[node['id']].append(connected_id)
                # Make it bidirectional
                if node['id'] not in graph[connected_id]:
                    graph[connected_id].append(node['id'])
        
        return graph
    
    def find_node_by_room(self, room_number: str) -> Optional[str]:
        """Find node ID that contains the given room number"""
        for node in self.nodes:
            if room_number in node['rooms']:
                return node['id']
        return None
    
    def find_node_by_name(self, name: str) -> Optional[str]:
        """Find node ID by name (case-insensitive, handles variations)"""
        # Normalize search string: lowercase, remove punctuation and spaces
        def normalize(s: str) -> str:
            s = s.lower().strip()
            # Remove common punctuation and spaces
            for char in ["'", ".", "-", " ", "_"]:
                s = s.replace(char, "")
            return s
        
        search_name = normalize(name)
        
        # First try exact match (case insensitive, original)
        for node in self.nodes:
            if node['name'].lower().strip() == name.lower().strip():
                return node['id']
            if node['id'].lower() == name.lower().strip():
                return node['id']
            
            # Check aliases if they exist
            if 'aliases' in node:
                for alias in node['aliases']:
                    if alias.lower().strip() == name.lower().strip():
                        return node['id']
        
        # Then try normalized exact match
        for node in self.nodes:
            node_name_normalized = normalize(node['name'])
            node_id_normalized = normalize(node['id'])
            if node_name_normalized == search_name or node_id_normalized == search_name:
                return node['id']
            
            # Check aliases with normalization
            if 'aliases' in node:
                for alias in node['aliases']:
                    if normalize(alias) == search_name:
                        return node['id']
        
        # Try partial match (normalized) - search in node name
        for node in self.nodes:
            node_name_normalized = normalize(node['name'])
            node_id_normalized = normalize(node['id'])
            if (search_name in node_name_normalized or 
                search_name in node_id_normalized):
                return node['id']
            
            # Check aliases for partial match
            if 'aliases' in node:
                for alias in node['aliases']:
                    alias_normalized = normalize(alias)
                    if search_name in alias_normalized or alias_normalized in search_name:
                        return node['id']
        
        # Try reverse partial match - node name in search (for abbreviations)
        if len(search_name) >= 4:  # Only for meaningful searches
            for node in self.nodes:
                node_name_normalized = normalize(node['name'])
                node_id_normalized = normalize(node['id'])
                if (node_name_normalized in search_name or 
                    node_id_normalized in search_name):
                    return node['id']
                
                # Check aliases for reverse partial match
                if 'aliases' in node:
                    for alias in node['aliases']:
                        alias_normalized = normalize(alias)
                        if alias_normalized in search_name or search_name in alias_normalized:
                            return node['id']
        
        return None
    
    def find_path_bfs(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """
        BFS - Finds shortest path (recommended for navigation)
        Returns list of node IDs from start to end
        """
        if start_id == end_id:
            return [start_id]
        
        # Queue stores paths: [(path1), (path2), ...]
        queue = deque([[start_id]])
        visited = {start_id}
        
        while queue:
            path = queue.popleft()
            current = path[-1]
            
            # Get neighbors
            neighbors = self.graph.get(current, [])
            
            for neighbor in neighbors:
                if neighbor == end_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None  # No path found
    
    def find_path_dfs(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """
        DFS - Explores one branch fully (for educational purposes)
        Returns list of node IDs from start to end
        """
        if start_id == end_id:
            return [start_id]
        
        visited = set()
        path = []
        
        def dfs(current: str) -> bool:
            if current == end_id:
                return True
            
            visited.add(current)
            path.append(current)
            
            neighbors = self.graph.get(current, [])
            for neighbor in neighbors:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
            
            path.pop()
            return False
        
        if dfs(start_id):
            return path + [end_id]
        
        return None
    
    def navigate(self, destination: str, use_dfs: bool = False) -> Dict:
        """
        Main navigation function - finds path to destination
        Uses BFS by default (shortest path)
        
        Args:
            destination: Room number (e.g., "101") or location name (e.g., "Library")
            use_dfs: If True, use DFS instead of BFS
        
        Returns:
            Dictionary with path information
        """
        destination_id = None
        start_id = self.start_node
        
        # Check if destination is a room number
        destination_id = self.find_node_by_room(destination)
        
        # If not a room, try finding by name
        if not destination_id:
            destination_id = self.find_node_by_name(destination)
        
        if not destination_id:
            return {
                'success': False,
                'error': f'Destination "{destination}" not found'
            }
        
        # Find path
        path = (self.find_path_dfs(start_id, destination_id) if use_dfs 
                else self.find_path_bfs(start_id, destination_id))
        
        if not path:
            return {
                'success': False,
                'error': f'No path found to {destination}'
            }
        
        # Get full node details for path
        path_nodes = []
        for node_id in path:
            node = next((n for n in self.nodes if n['id'] == node_id), None)
            if node:
                path_nodes.append(node)
        
        return {
            'success': True,
            'path': path,
            'path_nodes': path_nodes,
            'photos': [node['photo'] for node in path_nodes],
            'start': next((n for n in self.nodes if n['id'] == start_id), None),
            'destination': next((n for n in self.nodes if n['id'] == destination_id), None)
        }
    
    def recover_from_landmark(self, landmark_name: str) -> Dict:
        """
        Recovery function - reset navigation from a landmark
        Updates the start node to the landmark location
        """
        landmark_id = self.find_node_by_name(landmark_name)
        
        if not landmark_id:
            return {
                'success': False,
                'error': f'Landmark "{landmark_name}" not found'
            }
        
        # Update start node to the landmark
        self.start_node = landmark_id
        landmark_node = next((n for n in self.nodes if n['id'] == landmark_id), None)
        
        return {
            'success': True,
            'new_start': landmark_node
        }
    
    def get_available_destinations(self) -> List[Dict]:
        """Get all available destinations (rooms and landmarks)"""
        destinations = []
        
        for node in self.nodes:
            # Add rooms
            rooms = node.get('rooms', [])
            for room in rooms:
                destinations.append({
                    'type': 'room',
                    'value': room,
                    'location': node['name']
                })
            
            # Add landmarks and other location types (including pathways for important locations)
            if node.get('type') in ['landmark', 'hallway', 'stairs', 'elevator', 'pathway']:
                destinations.append({
                    'type': 'location',
                    'value': node['name'],
                    'location': node['name'],
                    'floor': node.get('floor', 1)
                })
        
        return destinations


if __name__ == "__main__":
    # Example usage
    nav = NavigationSystem('navigation_data.json')
    
    print("=== Navigation System Test ===\n")
    
    # Test 1: Navigate to a room
    print("Test 1: Navigate to Room 101")
    result = nav.navigate("101")
    if result['success']:
        print(f"Path: {' -> '.join([n['name'] for n in result['path_nodes']])}")
        print(f"Photos: {result['photos']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test 2: Navigate to a landmark
    print("Test 2: Navigate to Library")
    result = nav.navigate("Library")
    if result['success']:
        print(f"Path: {' -> '.join([n['name'] for n in result['path_nodes']])}")
        print(f"Photos: {result['photos']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test 3: Navigate to Student Association
    print("Test 3: Navigate to Student Association")
    result = nav.navigate("Student Association")
    if result['success']:
        print(f"Path: {' -> '.join([n['name'] for n in result['path_nodes']])}")
        print(f"Photos: {result['photos']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test 4: Recovery from landmark
    print("Test 4: Recovery - Reset from Library")
    recovery = nav.recover_from_landmark("Library")
    if recovery['success']:
        print(f"New start location: {recovery['new_start']['name']}")
        print("\nNow navigating to Room 101 from Library:")
        result = nav.navigate("101")
        if result['success']:
            print(f"Path: {' -> '.join([n['name'] for n in result['path_nodes']])}")
    else:
        print(f"Error: {recovery['error']}")

