"""
Simple test script for navigation system
Run this to test pathfinding
"""

from pathfinding import NavigationSystem

def main():
    # Initialize navigation system
    nav = NavigationSystem('navigation_data.json')
    
    print("=" * 60)
    print("Photo-Based Indoor Navigation System")
    print("=" * 60)
    print()
    
    # Show available destinations
    print("Available Destinations:")
    destinations = nav.get_available_destinations()
    for dest in destinations:
        print(f"  - {dest['value']} ({dest['type']}) - {dest['location']}")
    print()
    
    # Interactive navigation
    while True:
        print("-" * 60)
        destination = input("Enter destination (room number or location name, or 'quit' to exit): ").strip()
        
        if destination.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not destination:
            continue
        
        # Navigate
        result = nav.navigate(destination)
        
        if result['success']:
            print(f"\n✓ Path found!")
            print(f"  From: {result['start']['name']}")
            print(f"  To: {result['destination']['name']}")
            print(f"\n  Route:")
            for i, node in enumerate(result['path_nodes'], 1):
                print(f"    {i}. {node['name']} ({node['type']})")
                print(f"       Photo: {node['photo']}")
                if node['description']:
                    print(f"       {node['description']}")
            print(f"\n  Total steps: {len(result['path_nodes'])}")
        else:
            print(f"\n✗ {result['error']}")
        
        print()

if __name__ == "__main__":
    main()

