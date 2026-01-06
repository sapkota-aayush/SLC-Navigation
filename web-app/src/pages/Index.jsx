import { useState, useEffect, useRef } from "react";
import { MapPin, Navigation, ArrowLeft } from "lucide-react";
import { SimplePathViewer } from "@/components/navigation/SimplePathViewer";
import { cn } from "@/lib/utils";
import axios from "axios";

// API base URL - use environment variable or default to relative path
const API_URL = import.meta.env.VITE_API_URL || '';

// Configure axios to use API URL if provided
if (API_URL) {
  axios.defaults.baseURL = API_URL;
}

const Index = () => {
  const [showRoute, setShowRoute] = useState(false);
  const [routeInfo, setRouteInfo] = useState({ from: "", to: "", instructions: "" });
  const [searchQuery, setSearchQuery] = useState("");
  const [routeSteps, setRouteSteps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [destinations, setDestinations] = useState([]);
  const [focusedField, setFocusedField] = useState(null); // Track which field has focus
  const focusedFieldRef = useRef(null); // Ref to persist focus through click events

  // Fetch destinations on mount
  useEffect(() => {
    const fetchDestinations = async () => {
      try {
        const response = await axios.get('/api/destinations');
        if (response.data.success) {
          setDestinations(response.data.destinations || []);
        }
      } catch (err) {
        console.error('Failed to fetch destinations:', err);
      }
    };
    fetchDestinations();
  }, []);

  const handleSearch = async (to) => {
    if (!routeInfo.from || !to) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Use AI to interpret both start and destination queries
      let destination = to;
      let startLocation = routeInfo.from;
      
      // Interpret destination with AI (always try AI first, then fallback to direct)
      try {
        const searchResponse = await axios.post('/api/search', {
          query: to,
          type: 'destination'
        });
        
        if (searchResponse.data.success) {
          destination = searchResponse.data.name;
          // Update the search query to show the matched location
          setSearchQuery(destination);
        } else {
          // If AI search fails, try direct navigation with original query
          console.log('AI search returned no match, trying direct lookup');
        }
      } catch (searchErr) {
        // If AI search fails, try with original query
        console.log('AI search error, using original query:', searchErr);
      }
      
      // Interpret start location with AI if it's not "Main Entrance"
      if (startLocation && startLocation.trim() !== "" && startLocation !== "Main Entrance") {
        try {
          const startSearchResponse = await axios.post('/api/search', {
            query: startLocation,
            type: 'start'
          });
          
          if (startSearchResponse.data.success) {
            startLocation = startSearchResponse.data.name;
            setRouteInfo(prev => ({ ...prev, from: startLocation }));
          }
        } catch (startErr) {
          // If AI search fails, use original
          console.log('Start location AI search failed, using original:', startErr);
        }
      } else if (!startLocation || startLocation.trim() === "") {
        // Default to Main Entrance if empty
        startLocation = "Main Entrance";
        setRouteInfo(prev => ({ ...prev, from: startLocation }));
      }
      
      const response = await axios.post('/api/navigate', {
        start_location: startLocation,
        destination: destination,
      });

      if (response.data.success) {
        const pathNodes = response.data.path_nodes || [];
        const instructions = response.data.ai_instructions || "";
        
        // Convert path_nodes to route steps format
        const steps = pathNodes.map((node, index) => {
          // Determine direction based on node type and position
          let direction = "forward";
          if (node.type === "stairs" || node.type === "elevator") {
            direction = "stairs";
          } else if (index === pathNodes.length - 1) {
            direction = "destination";
          } else if (index === 0) {
            direction = "forward";
          } else {
            // Try to infer direction from description or connections
            const desc = (node.description || "").toLowerCase();
            if (desc.includes("right")) direction = "right";
            else if (desc.includes("left")) direction = "left";
            else direction = "forward";
          }

          // Construct image URL - handle both Supabase URLs and local paths
          let imageUrl = node.photo || "";
          if (imageUrl && !imageUrl.startsWith('http')) {
            // Local path - use /static/ prefix for development
            if (imageUrl.startsWith('images/')) {
              imageUrl = '/static/' + imageUrl.substring(7); // Remove 'images/' (7 chars)
            } else {
              imageUrl = '/static/' + imageUrl;
            }
          }
          // If it's already a Supabase URL (starts with http), use it directly

          return {
            id: node.id || `step-${index}`,
            title: node.name || "Unknown Location",
            imageUrl: imageUrl,
            direction: direction,
          };
        });

        setRouteSteps(steps);
        setRouteInfo(prev => ({ ...prev, to, instructions: instructions, pathNodes: pathNodes }));
        setShowRoute(true);
      } else {
        setError(response.data.error || "Failed to find route");
      }
    } catch (err) {
      console.error('Navigation error:', err);
      setError(err.response?.data?.error || "Failed to find route. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const filteredDestinations = destinations.filter(d => 
    d && d.value && d.value.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (showRoute && routeSteps.length > 0) {
    return (
      <div className="min-h-screen bg-background">
        {/* Minimal header */}
        <header className="sticky top-0 z-50 bg-card border-b border-border">
          <div className="px-2 py-1.5 flex items-center gap-2">
            <button
              onClick={() => {
                setShowRoute(false);
                setRouteSteps([]);
                setError(null);
              }}
              className="w-9 h-9 rounded-full bg-secondary flex items-center justify-center hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="nav-gradient p-1.5 rounded-md">
              <Navigation className="w-4 h-4 text-accent-foreground" />
            </div>
            <span className="font-display font-semibold text-sm text-foreground">SLC Navigator</span>
          </div>
        </header>

        <SimplePathViewer 
          steps={routeSteps} 
          from={routeInfo.from} 
          to={routeInfo.to}
          instructions={routeInfo.instructions || ""}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="px-2 py-1.5">
          <div className="flex items-center gap-1.5">
            <div className="bg-accent p-1.5 rounded-md shadow-sm">
              <Navigation className="w-3.5 h-3.5 text-accent-foreground" />
            </div>
            <div>
              <h1 className="font-display text-xs font-bold text-foreground">SLC Navigator</h1>
              <p className="text-[8px] text-muted-foreground">St. Lawrence College</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 px-2 py-2 flex flex-col">
        {/* Error message */}
        {error && (
          <div className="mb-1.5 p-1.5 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-[10px]">
            {error}
          </div>
        )}

        {/* Input boxes */}
        <div className="space-y-1.5 mb-2.5">
          {/* From */}
          <div className="relative">
            <div className="absolute left-2.5 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-accent" />
            <input
              type="text"
              value={routeInfo.from}
              onChange={(e) => setRouteInfo(prev => ({ ...prev, from: e.target.value }))}
              onFocus={() => {
                setFocusedField('from');
                focusedFieldRef.current = 'from';
              }}
              onBlur={() => {
                // Delay clearing focus to allow button click to check it first
                setTimeout(() => {
                  setFocusedField(null);
                  if (focusedFieldRef.current === 'from') {
                    focusedFieldRef.current = null;
                  }
                }, 100);
              }}
              data-field="from"
              placeholder="Where are you?"
              className="w-full pl-7 pr-2 py-2.5 bg-card rounded-md border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent transition-all"
              disabled={loading}
            />
          </div>
          
          {/* Connector line */}
          <div className="flex items-center gap-1.5 pl-3.5">
            <div className="w-0.5 h-3 bg-border rounded-full" />
          </div>
          
          {/* To */}
          <div className="relative">
            <MapPin className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-accent" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => {
                setFocusedField('to');
                focusedFieldRef.current = 'to';
              }}
              onBlur={() => {
                // Delay clearing focus to allow button click to check it first
                setTimeout(() => {
                  setFocusedField(null);
                  if (focusedFieldRef.current === 'to') {
                    focusedFieldRef.current = null;
                  }
                }, 100);
              }}
              data-field="to"
              placeholder="Where do you want to go?"
              className="w-full pl-7 pr-2 py-2.5 bg-card rounded-md border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent transition-all"
              disabled={loading}
            />
          </div>
        </div>

        {/* Go button */}
        {routeInfo.from && searchQuery && (
          <button
            onClick={() => handleSearch(searchQuery)}
            disabled={loading}
            className="w-full py-2 bg-accent text-accent-foreground rounded-md font-semibold text-xs shadow-sm active:scale-95 transition-all mb-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Finding route..." : "Get Directions"}
          </button>
        )}

        {/* Quick destinations */}
        {destinations.length > 0 && (
          <>
            <p className="text-[9px] text-muted-foreground mb-1">Popular destinations</p>
            <div className="space-y-1 flex-1 overflow-auto">
              {filteredDestinations.map((dest, idx) => (
                <button
                  key={`${dest.type}-${dest.value}-${dest.location || ''}-${idx}`}
                  onMouseDown={(e) => {
                    // Capture which field is focused BEFORE the blur event fires
                    const activeEl = document.activeElement;
                    if (activeEl?.placeholder === "Where are you?" || activeEl?.getAttribute('data-field') === 'from') {
                      focusedFieldRef.current = 'from';
                    } else if (activeEl?.placeholder === "Where do you want to go?" || activeEl?.getAttribute('data-field') === 'to') {
                      focusedFieldRef.current = 'to';
                    }
                  }}
                  onClick={() => {
                    // Use the ref which persists through blur events
                    if (focusedFieldRef.current === 'from') {
                      setRouteInfo(prev => ({ ...prev, from: dest.value }));
                    } else {
                      // Default: fill "Where do you want to go?" field
                      setSearchQuery(dest.value);
                    }
                  }}
                  className="w-full flex items-center gap-2 p-2 bg-card rounded-md border border-border hover:border-accent transition-all group"
                >
                  <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center group-hover:bg-accent/10 transition-colors shrink-0">
                    <MapPin className="w-4 h-4 text-muted-foreground group-hover:text-accent transition-colors" />
                  </div>
                  <div className="text-left flex-1 min-w-0">
                    <p className="font-medium text-foreground text-xs truncate">{dest.value}</p>
                    {dest.location && dest.location !== dest.value && (
                      <p className="text-[9px] text-muted-foreground truncate">{dest.location}</p>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default Index;

