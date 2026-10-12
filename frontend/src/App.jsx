import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8001";

export default function App() {
  const [videos, setVideos] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [playingVideo, setPlayingVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const [videoResponse, categoryResponse] = await Promise.all([
          fetch(`${API}/api/videos`),
          fetch(`${API}/api/categories`),
        ]);

        if (!videoResponse.ok || !categoryResponse.ok) {
          throw new Error("Could not load database records.");
        }

        setVideos(await videoResponse.json());
        setCategories(await categoryResponse.json());
      } catch (err) {
        console.error("API error:", err);
        setError(
          "Backend connect nahi ho raha. Check karo ki Python API port 8001 par running hai."
        );
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape") {
        setPlayingVideo(null);
        setSelectedVideo(null);
      }
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, []);

  const filteredVideos = videos.filter((video) => {
    const query = search.toLowerCase();

    const matchesSearch =
      (video.title || "").toLowerCase().includes(query) ||
      (video.description || "").toLowerCase().includes(query) ||
      (video.transcript || "").toLowerCase().includes(query);

    const matchesCategory =
      category === "all" ||
      String(video.category_id) === String(category);

    return matchesSearch && matchesCategory;
  });

  const formatDuration = (seconds = 0) => {
    const totalSeconds = Number(seconds) || 0;
    const minutes = Math.floor(totalSeconds / 60);
    const remainingSeconds = totalSeconds % 60;

    return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
  };

  const closePlayer = () => setPlayingVideo(null);
  const closeTranscript = () => setSelectedVideo(null);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">V</div>
          <span>
            Video<span className="brand-accent">Index</span>
          </span>
        </div>

        <p className="sidebar-label">WORKSPACE</p>

        <button
          className="nav-item active"
          onClick={() => {
            setCategory("all");
            setSearch("");
          }}
        >
          ▦ &nbsp; Video Library
        </button>

        <button
          className="nav-item"
          onClick={() => {
            setCategory("all");
            setSearch("");
          }}
        >
          ◫ &nbsp; All Videos
        </button>

        <p className="sidebar-label">YOUR DATABASE</p>

        <div className="sidebar-stat">
          <span>Video records</span>
          <strong>{videos.length}</strong>
        </div>

        <div className="sidebar-stat">
          <span>Categories</span>
          <strong>{categories.length}</strong>
        </div>

        <div className="sidebar-footer">
          <span className="status-dot" />
          MySQL database
          <small>{error ? "Connection issue" : "Connected through API"}</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">YOUR PERSONAL LIBRARY</p>
            <h1>Video Library</h1>
            <p className="subtitle">
              Find videos, explore topics, and read transcripts.
            </p>
          </div>

          <div className="profile-avatar">A</div>
        </header>

        <section className="welcome-banner">
          <div>
            <span className="banner-label">
              VIDEO INDEX · DATABASE PROJECT
            </span>
            <h2>Your knowledge, organized.</h2>
            <p>
              One place for your videos, metadata and searchable transcripts.
            </p>
          </div>

          <div className="banner-symbol">▶</div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <span>Total videos</span>
            <strong>{videos.length}</strong>
            <small>Stored in MySQL</small>
          </div>

          <div className="stat-card">
            <span>Categories</span>
            <strong>{categories.length}</strong>
            <small>Available topics</small>
          </div>

          <div className="stat-card">
            <span>Total views</span>
            <strong>
              {videos.reduce(
                (sum, video) => sum + Number(video.views || 0),
                0
              )}
            </strong>
            <small>Across all records</small>
          </div>
        </section>

        <section className="library-section">
          <div className="section-heading">
            <div>
              <h2>Explore your videos</h2>
              <p>Browse your database records.</p>
            </div>

            <span className="result-count">
              {filteredVideos.length} RESULTS
            </span>
          </div>

          <div className="filters">
            <div className="search-box">
              <span>⌕</span>
              <input
                type="text"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search titles, descriptions or transcripts..."
              />
            </div>

            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              <option value="all">All categories</option>

              {categories.map((item) => (
                <option key={item.category_id} value={item.category_id}>
                  {item.category_name}
                </option>
              ))}
            </select>
          </div>

          {loading && (
            <p className="message">Loading your video library...</p>
          )}

          {error && <p className="message error">{error}</p>}

          {!loading && !error && filteredVideos.length === 0 && (
            <div className="empty-state">
              <span>⌕</span>
              <h3>No videos found</h3>
              <p>Try another search or choose a different category.</p>
            </div>
          )}

          <div className="video-grid">
            {filteredVideos.map((video) => {
              const categoryName =
                categories.find(
                  (item) =>
                    String(item.category_id) === String(video.category_id)
                )?.category_name || "Uncategorized";

              return (
                <article className="video-card" key={video.video_id}>
                  <div
                    className="video-thumbnail"
                    onClick={() => setPlayingVideo(video)}
                    role="button"
                    tabIndex={0}
                    aria-label={`Play ${video.title}`}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        setPlayingVideo(video);
                      }
                    }}
                  >
                    <div className="thumbnail-orbit orbit-one" />
                    <div className="thumbnail-orbit orbit-two" />

                    <button
                      type="button"
                      className="play-symbol"
                      aria-label={`Play ${video.title}`}
                      onClick={(event) => {
                        event.stopPropagation();
                        setPlayingVideo(video);
                      }}
                    >
                      ▶
                    </button>

                    <span className="duration">
                      {formatDuration(video.duration)}
                    </span>
                  </div>

                  <div className="video-info">
                    <span className="category-pill">{categoryName}</span>

                    <h3>{video.title}</h3>

                    <p className="video-description">
                      {video.description || "No description available."}
                    </p>

                    <div className="video-meta">
                      <span>{video.language || "Language unknown"}</span>
                      <span>
                        {Number(video.views || 0).toLocaleString()} views
                      </span>
                    </div>

                    <button
                      type="button"
                      className="details-button"
                      onClick={() => setSelectedVideo(video)}
                    >
                      View transcript <span>↗</span>
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <footer className="page-footer">
          VIDEO INDEX <span>·</span> POWERED BY PYTHON & MYSQL
        </footer>
      </main>

      {selectedVideo && (
        <div className="modal-backdrop" onClick={closeTranscript}>
          <section
            className="transcript-modal"
            onClick={(event) => event.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Video transcript"
          >
            <button
              type="button"
              className="close-button"
              onClick={closeTranscript}
              aria-label="Close transcript"
            >
              ×
            </button>

            <span className="banner-label">VIDEO TRANSCRIPT</span>

            <h2>{selectedVideo.title}</h2>

            <p className="modal-description">
              {selectedVideo.description || "No description available."}
            </p>

            <div className="transcript-content">
              {selectedVideo.transcript || "No transcript available."}
            </div>

            <button
              type="button"
              className="details-button"
              onClick={closeTranscript}
            >
              Close transcript
            </button>
          </section>
        </div>
      )}

      {playingVideo && (
        <div className="modal-backdrop" onClick={closePlayer}>
          <section
            className="transcript-modal player-modal"
            onClick={(event) => event.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Video player"
          >
            <button
              type="button"
              className="close-button"
              onClick={closePlayer}
              aria-label="Close video player"
            >
              ×
            </button>

            <span className="banner-label">NOW PLAYING</span>

            <h2>{playingVideo.title}</h2>

            <video
              key={playingVideo.video_id}
              controls
              autoPlay
              playsInline
              preload="metadata"
              style={{
                display: "block",
                width: "100%",
                maxHeight: "65vh",
                background: "#000",
                borderRadius: "12px",
                margin: "16px 0",
              }}
              onError={(event) => {
                console.error(
                  "Video playback error:",
                  event.currentTarget.error
                );
              }}
            >
              <source
                src={`${API}/api/videos/${playingVideo.video_id}/play`}
                type="video/mp4"
              />
              Your browser does not support HTML video.
            </video>

            <p className="modal-description">
              {playingVideo.description || "No description available."}
            </p>

                      <section className="player-transcript">
            <div className="transcript-heading">
              <div>
                <span className="banner-label">AI-GENERATED TRANSCRIPT</span>
                <h3>Video transcript</h3>
              </div>

              <button
                type="button"
                className="details-button"
                onClick={() => {
                  const text = playingVideo.transcript || "";
                  if (text) {
                    navigator.clipboard.writeText(text).catch(console.error);
                  }
                }}
                disabled={!playingVideo.transcript}
              >
                Copy transcript
              </button>
            </div>

            <div className="transcript-content">
              {playingVideo.transcript?.trim()
                ? playingVideo.transcript
                : "Transcript abhi available nahi hai."}
            </div>
          </section>
          </section>
        </div>
      )}
    </div>
  );
}