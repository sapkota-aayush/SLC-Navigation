"""
Test script for AI navigation features
"""

from ai_navigation import AINavigationSystem
import os

def main():
    print("=" * 60)
    print("AI-Powered Navigation System Test")
    print("=" * 60)
    print()
    
    # Initialize AI navigation system
    ai_nav = AINavigationSystem('navigation_data.json')
    
    if not ai_nav.ai_enabled:
        print("⚠️  AI features not enabled!")
        print("Make sure OPENAI_API_KEY is set in .env file")
        return
    
    print("✓ AI features enabled\n")
    
    # Test 1: Get navigation instructions with AI
    print("-" * 60)
    print("Test 1: AI Navigation Instructions to Room 101")
    print("-" * 60)
    
    result = ai_nav.get_navigation_instructions("101", use_ai=True)
    
    if result['success']:
        print(f"\n📍 Path: {' -> '.join([n['name'] for n in result['path_nodes']])}")
        print(f"\n📸 Photos: {len(result['photos'])} images")
        for i, photo in enumerate(result['photos'], 1):
            print(f"   {i}. {photo}")
        
        if 'ai_instructions' in result and result['ai_instructions']:
            print(f"\n🤖 AI Instructions:")
            print(result['ai_instructions'])
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test 2: Navigate to Student Association
    print("-" * 60)
    print("Test 2: AI Navigation Instructions to Student Association")
    print("-" * 60)
    
    result = ai_nav.get_navigation_instructions("Student Association", use_ai=True)
    
    if result['success']:
        print(f"\n📍 Path: {' -> '.join([n['name'] for n in result['path_nodes']])}")
        
        if 'ai_instructions' in result and result['ai_instructions']:
            print(f"\n🤖 AI Instructions:")
            print(result['ai_instructions'])
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test 3: Photo recognition (if user provides a photo)
    print("-" * 60)
    print("Test 3: Photo Recognition (Recovery Feature)")
    print("-" * 60)
    print("\nTo test photo recognition, you need to provide a photo path.")
    print("Example: python3 test_ai_navigation.py --photo images/library.webp")
    
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == '--photo':
        photo_path = sys.argv[2]
        print(f"\n🔍 Identifying location from photo: {photo_path}")
        
        identification = ai_nav.identify_location_from_photo(photo_path)
        
        if identification['success']:
            print(f"✓ Identified: {identification['location']['name']}")
            print(f"  Confidence: {identification.get('identified_name', 'N/A')}")
            
            # Test recovery
            recovery = ai_nav.recover_from_photo(photo_path)
            if recovery['success']:
                print(f"\n✓ Navigation reset from: {recovery['identified_location']['name']}")
                print(f"  New start: {recovery['new_start']['name']}")
        else:
            print(f"❌ {identification['error']}")

if __name__ == "__main__":
    main()

