import { useState, useRef, useEffect } from "react";
import { ChevronLeft, ChevronRight, MapPin, ArrowUp, CornerUpRight, CornerUpLeft, TrendingUp, Navigation, MessageSquare, X } from "lucide-react";
import { cn } from "@/lib/utils";

const directionIcons = {
  forward: ArrowUp,
  right: CornerUpRight,
  left: CornerUpLeft,
  stairs: TrendingUp,
  destination: MapPin,
};

const directionLabels = {
  forward: "Go straight",
  right: "Turn right",
  left: "Turn left",
  stairs: "Take stairs",
  destination: "You've arrived!",
};

export const SimplePathViewer = ({ steps, from, to, instructions = "" }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showInstructions, setShowInstructions] = useState(false);
  const [imageRotation, setImageRotation] = useState(0);
  const imgRef = useRef(null);
  
  const step = steps[currentStep];
  const DirectionIcon = directionIcons[step.direction];
  const progress = ((currentStep + 1) / steps.length) * 100;

  // Handle image orientation on load
  const handleImageLoad = (e) => {
    const img = e.target;
    if (img.naturalWidth && img.naturalHeight) {
      // If image is landscape (wider than tall), rotate it 90 degrees
      if (img.naturalWidth > img.naturalHeight) {
        setImageRotation(90);
      } else {
        setImageRotation(0);
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background relative">
      {/* Compact Header - Hidden when instructions are open */}
      {!showInstructions && (
        <div className="px-2 py-1 bg-card border-b border-border flex items-center gap-1.5 shrink-0">
          <Navigation className="w-3 h-3 text-accent shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1 text-[9px]">
              <span className="truncate font-medium">{from}</span>
              <span className="text-accent">→</span>
              <span className="truncate font-medium">{to}</span>
            </div>
            {/* Progress bar */}
            <div className="h-0.5 bg-muted rounded-full mt-1">
              <div 
                className="h-full bg-accent rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            {instructions && instructions.trim() && (
              <button
                onClick={() => setShowInstructions(!showInstructions)}
                className={cn(
                  "flex items-center gap-1.5 px-2.5 py-1 rounded-full transition-all",
                  "bg-accent/15 hover:bg-accent/25 text-accent border border-accent/30"
                )}
                title="Show text instructions"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span className="text-[9px] font-semibold hidden sm:inline">Text Guide</span>
              </button>
            )}
            <span className="text-[9px] font-bold text-accent shrink-0">{currentStep + 1}/{steps.length}</span>
          </div>
        </div>
      )}

      {/* Large Image Area - Takes most of the screen - Hidden when instructions are open */}
      {!showInstructions && (
      <div className="flex-1 relative bg-black min-h-0 flex items-center justify-center">
        <div className="w-full max-w-md mx-auto aspect-[3/4] relative overflow-hidden">
          <img
            ref={imgRef}
            src={step.imageUrl}
            alt={step.title}
            className="w-full h-full object-contain"
            style={{
              imageOrientation: 'from-image',
              transform: imageRotation ? `rotate(${imageRotation}deg)` : 'none',
              transition: 'transform 0.3s ease'
            }}
            onLoad={handleImageLoad}
          onError={(e) => {
            console.error('Image failed to load:', step.imageUrl);
            // Try direct backend URL if proxy fails
            if (step.imageUrl.startsWith('/static/')) {
              const backendUrl = 'http://localhost:5001' + step.imageUrl;
              console.log('Trying backend URL:', backendUrl);
              e.target.src = backendUrl;
              e.target.onerror = () => {
                e.target.onerror = null;
                e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ccc" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="16"%3EImage not found%3C/text%3E%3C/svg%3E';
              };
            } else {
              e.target.onerror = null;
              e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ccc" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em" font-size="16"%3EImage not found%3C/text%3E%3C/svg%3E';
            }
          }}
          />
        </div>
        
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40 pointer-events-none" />

        {/* Direction indicator - top center */}
        <div className={cn(
          "absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 rounded-full shadow-lg font-semibold text-sm z-10",
          step.direction === "destination" 
            ? "bg-green-500 text-white" 
            : "bg-accent text-accent-foreground"
        )}>
          <DirectionIcon className="w-4 h-4" />
          <span>{directionLabels[step.direction]}</span>
        </div>

        {/* Side navigation arrows */}
        {currentStep > 0 && (
          <button
            onClick={() => setCurrentStep(s => s - 1)}
            className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/90 backdrop-blur flex items-center justify-center shadow-md active:scale-95 z-10"
          >
            <ChevronLeft className="w-5 h-5 text-foreground" />
          </button>
        )}
        
        {currentStep < steps.length - 1 && (
          <button
            onClick={() => setCurrentStep(s => s + 1)}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-accent text-accent-foreground flex items-center justify-center shadow-md active:scale-95 z-10"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        )}

        {/* Location info - bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/95 via-black/60 to-transparent">
          <p className="text-white/70 text-[10px] mb-0.5">Step {currentStep + 1}</p>
          <h2 className="text-white font-display text-base font-bold">{step.title}</h2>
        </div>

        {/* Floating Instructions Button */}
        {instructions && instructions.trim() && (
          <button
            onClick={() => setShowInstructions(true)}
            className="absolute bottom-16 right-3 bg-accent text-accent-foreground px-4 py-2.5 rounded-full shadow-lg flex items-center gap-2 z-20 hover:shadow-xl active:scale-95 transition-all"
          >
            <MessageSquare className="w-4 h-4" />
            <span className="text-xs font-semibold">View Text Instructions</span>
          </button>
        )}
      </div>
      )}

      {/* AI Instructions Panel - Full screen overlay */}
      {showInstructions && instructions && (
        <div className="fixed inset-0 bg-black z-50 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10 shrink-0 bg-black">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-accent" />
              <h3 className="text-white font-semibold text-base">AI Text Instructions</h3>
            </div>
            <button
              onClick={() => setShowInstructions(false)}
              className="w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
              aria-label="Close instructions"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
          
          {/* Instructions Content */}
          <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-black to-gray-900">
            <div className="max-w-2xl mx-auto">
              <p className="text-white/90 text-base leading-relaxed whitespace-pre-wrap">
                {instructions}
              </p>
            </div>
          </div>
          
          {/* Footer with close button */}
          <div className="p-4 border-t border-white/10 shrink-0 bg-black">
            <button
              onClick={() => setShowInstructions(false)}
              className="w-full bg-accent text-accent-foreground py-3 rounded-lg font-semibold hover:bg-accent/90 transition-colors"
            >
              Close Instructions
            </button>
          </div>
        </div>
      )}

      {/* Thumbnail strip - Compact at bottom - Hidden when instructions are open */}
      {!showInstructions && (
      <div className="bg-card border-t border-border p-1 shrink-0">
        <div className="flex items-center gap-0.5 overflow-x-auto scrollbar-hide">
          {steps.map((s, index) => {
            const isActive = index === currentStep;
            const isPast = index < currentStep;
            
            return (
              <div key={s.id} className="flex items-center shrink-0">
                <button
                  onClick={() => setCurrentStep(index)}
                  className={cn(
                    "relative rounded overflow-hidden transition-all",
                    isActive 
                      ? "w-12 h-8 ring-1 ring-accent" 
                      : "w-9 h-6"
                  )}
                >
                  <img 
                    src={s.imageUrl} 
                    alt=""
                    className="w-full h-full object-cover aspect-[3/4]"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="75"%3E%3Crect fill="%23ccc" width="100" height="75"/%3E%3C/svg%3E';
                    }}
                  />
                  <div className={cn(
                    "absolute inset-0 flex items-center justify-center text-white text-[9px] font-bold",
                    isPast ? "bg-accent/70" : isActive ? "bg-transparent" : "bg-black/50"
                  )}>
                    {!isActive && (isPast ? "✓" : index + 1)}
                  </div>
                </button>
                
                {index < steps.length - 1 && (
                  <div className={cn(
                    "w-1 h-0.5 mx-0.5",
                    isPast ? "bg-accent" : "bg-border"
                  )} />
                )}
              </div>
            );
          })}
        </div>
        </div>
      )}

    </div>
  );
};

