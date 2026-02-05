import { useState, useEffect, useRef } from "react";
import { MapPin, ArrowLeft, X } from "lucide-react";
import { SimplePathViewer } from "@/components/navigation/SimplePathViewer";
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
        }
      } catch (searchErr) {
        // If AI search fails, try with original query
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
        
        // Removed direction parsing - we don't show turn indicators anymore to avoid confusion
        // Users follow the images instead of turn indicators

        // Convert path_nodes to route steps format with improved direction detection
        const steps = pathNodes.map((node, index) => {
          // Last node is always destination
          if (index === pathNodes.length - 1) {
            return {
              id: node.id || `step-${index}`,
              title: node.name || "Unknown Location",
              imageUrl: node.photo || "",
              direction: "destination",
            };
          }

          // Simplified direction - no turn indicators to avoid confusion
          // Only show stairs/elevator and destination indicators
          let direction = "forward"; // Hidden for regular steps - no indicator shown
          
          if (node.type === "stairs" || node.type === "elevator") {
            direction = "stairs"; // Show "Take stairs" indicator
          }
          // All other steps use "forward" but indicator is hidden (only shows for destination/stairs)

          // Construct image URL - handle both Supabase URLs and local paths
          let imageUrl = node.photo || "";
          if (imageUrl && !imageUrl.startsWith('http')) {
            // Local path - use /static/ prefix for development
            if (imageUrl.startsWith('images/')) {
              imageUrl = '/static/' + imageUrl.substring(7); // Remove 'images/' (7 chars)
            } else {
              imageUrl = '/static/' + imageUrl;
            }
          } else if (imageUrl && imageUrl.startsWith('http') && imageUrl.includes('supabase.co')) {
            // Convert Supabase URLs to WebP via backend conversion endpoint
            const apiBase = API_URL || '';
            imageUrl = `${apiBase}/api/image/webp?url=${encodeURIComponent(imageUrl)}&quality=80&max_width=1200`;
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
      <div className="min-h-screen bg-white">
        {/* Minimal header */}
        <header className="sticky top-0 z-50 bg-card border-b border-border">
          <div className="px-2 py-1.5 flex items-center gap-2">
            <button
              onClick={() => {
                setShowRoute(false);
                setRouteSteps([]);
                setError(null);
                setRouteInfo({ from: "", to: "", instructions: "" });
                setSearchQuery("");
              }}
              className="w-9 h-9 rounded-full bg-secondary flex items-center justify-center hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <img src="/slcNavLogo.png" alt="SLC Navigator Logo" className="w-10 h-10 object-contain" />
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
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="px-3 py-2">
          <div className="flex items-center gap-2.5">
            <img src="/slcNavLogo.png" alt="SLC Navigator Logo" className="w-10 h-10 object-contain" />
            <div>
              <h1 className="font-display text-sm font-bold text-foreground leading-tight">SLC Navigator</h1>
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
              className="w-full pl-7 pr-10 py-3 bg-card rounded-md border border-border text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent transition-all"
              disabled={loading}
            />
            {routeInfo.from && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setRouteInfo(prev => ({ ...prev, from: "" }));
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-muted hover:bg-accent/20 flex items-center justify-center transition-colors"
                aria-label="Clear"
              >
                <X className="w-3.5 h-3.5 text-muted-foreground hover:text-foreground" />
              </button>
            )}
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
              className="w-full pl-7 pr-10 py-3 bg-card rounded-md border border-border text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent transition-all"
              disabled={loading}
            />
            {searchQuery && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setSearchQuery("");
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-muted hover:bg-accent/20 flex items-center justify-center transition-colors"
                aria-label="Clear"
              >
                <X className="w-3.5 h-3.5 text-muted-foreground hover:text-foreground" />
              </button>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 mb-2.5">
          {(routeInfo.from || searchQuery) && (
            <button
              onClick={() => {
                setRouteInfo({ from: "", to: "", instructions: "" });
                setSearchQuery("");
                setError(null);
              }}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md font-semibold text-xs shadow-sm active:scale-95 transition-all hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Clear
            </button>
          )}
          {routeInfo.from && searchQuery && (
            <button
              onClick={() => handleSearch(searchQuery)}
              disabled={loading}
              className="flex-1 py-2 bg-accent text-accent-foreground rounded-md font-semibold text-xs shadow-sm active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Finding route..." : "Get Directions"}
            </button>
          )}
        </div>

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

        {/* Disclaimer watermark */}
        <p className="mt-auto pt-4 pb-2 px-3 text-[10px] text-muted-foreground/80 text-center">
          Individual student project. Not affiliated with St. Lawrence College.
        </p>
      </main>
    </div>
  );
};

export default Index;

