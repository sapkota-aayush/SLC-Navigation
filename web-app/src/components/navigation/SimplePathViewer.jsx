import { useState, useRef, useEffect } from "react";
import { ChevronLeft, ChevronRight, MapPin, ArrowUp, CornerUpRight, CornerUpLeft, TrendingUp, Navigation, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

const directionIcons = {
  forward: ArrowUp,
  right: CornerUpRight,
  left: CornerUpLeft,
  stairs: TrendingUp,
  destination: MapPin,
};

const directionLabels = {
  forward: "Continue",
  right: "Turn right",
  left: "Turn left",
  stairs: "Take stairs",
  destination: "You've arrived!",
};

export const SimplePathViewer = ({ steps, from, to, instructions = "" }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [imageRotation, setImageRotation] = useState(0);
  const [imageScale, setImageScale] = useState({ x: 1, y: 1 });
  const imgRef = useRef(null);
  
  const step = steps[currentStep];
  const DirectionIcon = directionIcons[step.direction];
  const progress = ((currentStep + 1) / steps.length) * 100;

  // Handle image orientation on load - reset rotation when step changes
  useEffect(() => {
    setImageRotation(0);
    setImageScale({ x: 1, y: 1 });
  }, [currentStep]);

  // Handle image orientation on load - simple aspect ratio detection
  const handleImageLoad = (e) => {
    const img = e.target;
    
    // Simple check: if image is landscape (wider than tall), rotate to portrait
    if (img.naturalWidth && img.naturalHeight && img.naturalWidth > img.naturalHeight) {
      setImageRotation(90);
    } else {
      setImageRotation(0);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white relative overflow-hidden">
      {/* Header - Always visible */}
      <div className="px-4 py-3 bg-card border-b border-border flex items-center gap-3 shrink-0">
        <Navigation className="w-5 h-5 text-accent shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-sm">
            <span className="truncate font-medium">{from}</span>
            <span className="text-accent text-lg">→</span>
            <span className="truncate font-medium">{to}</span>
          </div>
          {/* Progress bar */}
          <div className="h-1.5 bg-muted rounded-full mt-2">
            <div 
              className="h-full bg-accent rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        <span className="text-sm font-bold text-accent shrink-0">{currentStep + 1}/{steps.length}</span>
      </div>

      {/* Main Content Area - Image and Instructions together */}
      <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
        {/* Image Area - Smaller to make room for instructions */}
        <div className="relative bg-white flex items-center justify-center py-3 px-4 shrink-0">
          <div className="w-full max-w-[280px] sm:max-w-sm mx-auto aspect-[3/4] relative overflow-hidden rounded-xl shadow-xl border-2 border-border/50 max-h-[45vh] sm:max-h-[50vh]">
            <img
              ref={imgRef}
              src={step.imageUrl}
              alt={step.title}
              className="w-full h-full object-contain"
              style={{
                imageOrientation: 'from-image',
                transform: `rotate(${imageRotation}deg) scaleX(${imageScale.x}) scaleY(${imageScale.y})`,
                transformOrigin: 'center center',
                transition: 'transform 0.3s ease'
              }}
              onLoad={handleImageLoad}
              onError={(e) => {
                console.error('Image failed to load:', step.imageUrl);
                if (step.imageUrl.startsWith('/static/')) {
                  const backendUrl = 'http://localhost:8000' + step.imageUrl;
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
            
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40 pointer-events-none rounded-xl" />

            {/* Direction indicator - Only show for destination or stairs */}
            {(step.direction === "destination" || step.direction === "stairs") && (
              <div className={cn(
                "absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 rounded-full shadow-lg font-semibold text-sm z-10 backdrop-blur-sm",
                step.direction === "destination" 
                  ? "bg-green-500/90 text-white" 
                  : "bg-accent/85 text-accent-foreground"
              )}>
                <DirectionIcon className="w-4 h-4" />
                <span>{directionLabels[step.direction]}</span>
              </div>
            )}

            {/* Side navigation arrows */}
            {currentStep > 0 && (
              <button
                onClick={() => setCurrentStep(s => s - 1)}
                className="absolute left-4 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full bg-white/95 backdrop-blur-md flex items-center justify-center shadow-lg active:scale-95 z-10 transition-all hover:scale-105"
              >
                <ChevronLeft className="w-7 h-7 text-foreground" />
              </button>
            )}
            
            {currentStep < steps.length - 1 && (
              <button
                onClick={() => setCurrentStep(s => s + 1)}
                className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full bg-accent text-accent-foreground flex items-center justify-center shadow-lg active:scale-95 z-10 transition-all hover:scale-105"
              >
                <ChevronRight className="w-7 h-7" />
              </button>
            )}

            {/* Location info - bottom */}
            <div className="absolute bottom-0 left-0 right-0 p-5 bg-gradient-to-t from-black/95 via-black/60 to-transparent rounded-b-xl">
              <p className="text-white/70 text-xs mb-1">Step {currentStep + 1}</p>
              <h2 className="text-white font-display text-lg font-bold break-words whitespace-normal leading-tight" title={step.title}>
                {step.title}
              </h2>
            </div>
          </div>
        </div>

        {/* Instructions Panel - Always visible below image if instructions exist */}
        {instructions && instructions.trim() ? (
          <div className="flex-1 min-h-0 bg-gradient-to-b from-card to-background border-t border-border overflow-y-auto">
            <div className="p-3 sm:p-4 max-w-2xl mx-auto">
              <div className="flex items-center gap-2 mb-2 sm:mb-3 shrink-0">
                <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-accent" />
                <h3 className="text-foreground font-semibold text-sm sm:text-base">Directions</h3>
              </div>
              <div className="bg-white/50 backdrop-blur-sm rounded-lg p-3 sm:p-4 border border-border/50 shadow-sm">
                <p className="text-foreground/90 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">
                  {instructions}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 min-h-0 flex items-center justify-center p-4">
            <p className="text-muted-foreground text-sm">Loading directions...</p>
          </div>
        )}
      </div>

      {/* Thumbnail strip - At bottom */}
      <div className="bg-card border-t border-border p-3 shrink-0">
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
          {steps.map((s, index) => {
            const isActive = index === currentStep;
            const isPast = index < currentStep;
            
            return (
              <div key={s.id} className="flex items-center shrink-0">
                <button
                  onClick={() => setCurrentStep(index)}
                  className={cn(
                    "relative rounded-lg overflow-hidden transition-all",
                    isActive 
                      ? "w-16 h-12 ring-2 ring-accent shadow-lg" 
                      : "w-12 h-9"
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
                    "absolute inset-0 flex items-center justify-center text-white text-xs font-bold",
                    isPast ? "bg-accent/70" : isActive ? "bg-transparent" : "bg-black/50"
                  )}>
                    {!isActive && (isPast ? "✓" : index + 1)}
                  </div>
                </button>
                
                {index < steps.length - 1 && (
                  <div className={cn(
                    "w-2 h-1 mx-1 rounded-full",
                    isPast ? "bg-accent" : "bg-border"
                  )} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Review call-to-action */}
      <div className="bg-background border-t border-border px-4 py-3 text-center text-xs text-muted-foreground">
        <p className="font-medium text-foreground mb-1">Please leave a review</p>
        <p className="mb-2">
          Your feedback helps us improve SLC Navigator and make it better for everyone.
        </p>
        <a
          href="/review"
          className="inline-flex items-center justify-center px-3 py-1.5 rounded-md bg-accent text-accent-foreground text-xs font-semibold shadow-sm active:scale-95 transition-all hover:bg-accent/90"
        >
          Go to review page
        </a>
      </div>

    </div>
  );
};

