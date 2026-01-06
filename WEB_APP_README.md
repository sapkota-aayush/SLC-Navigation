# Web Interface - Quick Start Guide

## 🚀 Starting the Application

### Option 1: Use the start script (Recommended)
```bash
./start.sh
```

### Option 2: Manual start

**Terminal 1 - Start Flask API:**
```bash
python3 api_server.py
```

**Terminal 2 - Start React Frontend:**
```bash
cd web-app
npm run dev
```

## 📍 Access Points

- **Web Interface**: http://localhost:5173
- **API Server**: http://localhost:5000

## 🎯 How to Use

1. **Enter Destination**: Type a room number (e.g., "101") or location name (e.g., "Library")
2. **Click Navigate**: The system will find the shortest path
3. **View Route**: See step-by-step path with photos
4. **Browse Photos**: Use arrow buttons to navigate through the photo sequence
5. **Read Instructions**: AI-generated navigation instructions appear below

## 📸 Adding the Stairs Image

When you add the stairs image:
1. Save it as `stairs.jpg` in the `images/` folder
2. The system will automatically use it (already configured in JSON)

## 🛠️ Troubleshooting

**Images not showing?**
- Make sure Flask API is running (port 5000)
- Check that images are in the `images/` folder
- Verify image filenames match the JSON

**API connection error?**
- Ensure Flask server is running: `python3 api_server.py`
- Check that port 5000 is not in use

**AI features not working?**
- Verify `.env` file exists with `OPENAI_API_KEY`
- Check API key is valid

