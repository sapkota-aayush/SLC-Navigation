# Photo-Based Indoor Navigation System

A visual navigation system that uses real-world photographs to guide users through buildings, replacing complex 3D maps or GPS.

## Project Structure

```
SLC-Navigation/
├── images/                    # All navigation photos
│   ├── Main Intrance.jpg
│   ├── Davies+hall.webp
│   ├── library.webp
│   ├── Student assocaition.jpg
│   ├── Cafeteria.jpeg
│   └── ...
├── navigation_data.json       # Map structure (nodes, connections, rooms)
├── pathfinding.py            # BFS/DFS pathfinding implementation
├── ai_navigation.py          # AI-powered features (image recognition)
├── test_navigation.py        # Interactive test script
├── test_ai_navigation.py     # AI features test script
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not in git)
└── README.md
```

## How It Works

1. **Graph Structure**: Locations are nodes, connections are edges
2. **Pathfinding**: Uses BFS (Breadth-First Search) to find shortest path
3. **Photo Sequence**: Returns sequence of photos showing the route
4. **Recovery**: Users can reset navigation from any visible landmark
5. **AI Recognition**: Uses OpenAI Vision API to identify location from user photos
6. **AI Instructions**: Generates natural language navigation directions

## Setup

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Set up API key (create `.env` file):
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Quick Test (Basic Pathfinding)
```bash
python3 pathfinding.py
```

### Interactive Navigation
```bash
python3 test_navigation.py
```

Then enter:
- Room numbers: `101`, `102`
- Location names: `Library`, `Cafeteria`, `Student Association`

### AI Features Test
```bash
python3 test_ai_navigation.py
```

Test photo recognition:
```bash
python3 test_ai_navigation.py --photo images/library.webp
```

### In Your Code

**Basic Navigation:**
```python
from pathfinding import NavigationSystem

# Initialize
nav = NavigationSystem('navigation_data.json')

# Navigate to a room
result = nav.navigate("101")
if result['success']:
    print(f"Path: {result['path']}")
    print(f"Photos: {result['photos']}")

# Recovery from landmark
nav.recover_from_landmark("Library")
result = nav.navigate("101")  # Now starts from Library
```

**AI-Powered Navigation:**
```python
from ai_navigation import AINavigationSystem

# Initialize with AI
ai_nav = AINavigationSystem('navigation_data.json')

# Get AI-generated navigation instructions
result = ai_nav.get_navigation_instructions("101", use_ai=True)
if result['success']:
    print(result['ai_instructions'])

# Photo recognition (recovery)
recovery = ai_nav.recover_from_photo("user_photo.jpg")
if recovery['success']:
    print(f"Identified location: {recovery['identified_location']['name']}")
    # Now navigate from this location
    result = ai_nav.navigate("101")
```

## Features

- ✅ BFS pathfinding (shortest path)
- ✅ DFS pathfinding (for comparison)
- ✅ Room number lookup
- ✅ Location name search
- ✅ Recovery system (reset from landmark)
- ✅ Photo sequence generation
- ✅ **AI image recognition** (identify location from user photos)
- ✅ **AI-generated navigation instructions** (natural language directions)

## AI Features

### Image Recognition
Users can take a photo of their current location, and the AI will:
- Compare it with all navigation photos
- Identify which landmark/location they're at
- Automatically reset navigation from that point

### Navigation Instructions
The AI generates step-by-step directions:
- Clear instructions (left, right, straight, up stairs)
- What to look for (landmarks, signs, features)
- Friendly, easy-to-follow format

## Next Steps

- [ ] Create web/mobile UI
- [ ] Add more locations and photos
- [ ] Improve AI recognition accuracy
- [ ] Add voice navigation

