import { useState } from "react";

const Review = () => {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [title, setTitle] = useState("");
  const [comment, setComment] = useState("");

  const stars = [1, 2, 3, 4, 5];

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <header className="bg-card border-b border-border">
        <div className="px-3 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img src="/slcNavLogo.png" alt="SLC Navigator Logo" className="w-10 h-10 object-contain" />
            <div>
              <h1 className="font-display text-sm font-bold text-foreground leading-tight">
                SLC Navigator
              </h1>
              <p className="text-[10px] text-muted-foreground">Share your experience</p>
            </div>
          </div>
          <a
            href="/"
            className="text-[10px] text-accent underline hover:no-underline font-medium"
          >
            Back to app
          </a>
        </div>
      </header>

      <main className="flex-1 px-3 py-4 max-w-md w-full mx-auto">
        <section className="mb-4">
          <h2 className="text-base font-semibold text-foreground mb-1">
            Please leave a review
          </h2>
          <p className="text-[12px] text-muted-foreground">
            Your feedback helps us improve SLC Navigator and make it better for everyone.
          </p>
        </section>

        <form className="space-y-4">
          {/* Star rating */}
          <div>
            <label className="block text-[11px] font-medium text-foreground mb-1.5">
              Rating
            </label>
            <div className="flex items-center gap-1.5">
              {stars.map((star) => {
                const active = (hoverRating || rating) >= star;
                return (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="w-7 h-7 flex items-center justify-center"
                    aria-label={`${star} star${star > 1 ? "s" : ""}`}
                  >
                    <span
                      className={`text-lg ${
                        active ? "text-yellow-500" : "text-muted-foreground"
                      }`}
                    >
                      ★
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Review title */}
          <div>
            <label className="block text-[11px] font-medium text-foreground mb-1.5">
              Review title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Short summary of your experience"
              className="w-full px-3 py-2 rounded-md border border-border text-[12px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent bg-card"
            />
          </div>

          {/* Comment */}
          <div>
            <label className="block text-[11px] font-medium text-foreground mb-1.5">
              Comment
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              placeholder="Tell us what worked well and what could be improved"
              className="w-full px-3 py-2 rounded-md border border-border text-[12px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent bg-card resize-none"
            />
          </div>

          {/* Submit (placeholder only – hook up to backend later) */}
          <button
            type="button"
            className="w-full py-2 rounded-md bg-accent text-accent-foreground text-[12px] font-semibold shadow-sm active:scale-95 transition-all hover:bg-accent/90"
          >
            Submit review
          </button>

          <p className="text-[10px] text-muted-foreground text-center mt-1">
            This is an individual student project. Not affiliated with St. Lawrence College.
          </p>
        </form>
      </main>
    </div>
  );
};

export default Review;

