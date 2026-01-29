"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import Row from "@/components/Row";
import ArticleModal from "@/components/ArticleModal";
import {
  getRecommendations,
  logClick,
  getRecentClicks,
  type RecommendationItem,
  type RecommendationResponse,
} from "@/lib/api";

function uuid() {
  return crypto.randomUUID();
}

const LS_KEY = "newsflix_prefs_v1";

export default function HomePage() {
  const [anonId, setAnonId] = useState<string>(() => `anon_${Math.random().toString(16).slice(2, 8)}`);
  const [sessionId, setSessionId] = useState<string>(() => uuid());

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string>("");

  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<RecommendationItem | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const [devMode, setDevMode] = useState(false);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  // REAL “Because you clicked” data
  const [becauseData, setBecauseData] = useState<RecommendationResponse | null>(null);

  const items = data?.items ?? [];
  const impressionId = data?.impression_id ?? null;

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((x) => (x.title || "").toLowerCase().includes(q));
  }, [items, query]);

  const hero = filtered[0] || null;
  const row1 = filtered.slice(0, 12);
  const row2 = filtered.slice(12, 24);

  const becauseItems = becauseData?.items ?? [];

  // Saved row (from localStorage)
  const savedItems = useMemo(() => {
    if (!savedIds.size) return [];
    return items.filter((it) => savedIds.has(it.item_id));
  }, [items, savedIds]);

  async function loadFeed() {
    setLoading(true);
    setError("");
    try {
      const res = await getRecommendations({
        anonymous_id: anonId,
        session_id: sessionId,
        device_type: "web",
        app_version: "nextjs",
        user_agent: "recsys-frontend",
        referrer: "home",
        page_size: 36,
        surface: "for_you",
        locale: "en-US",
      });
      setData(res);
    } catch (e: any) {
      setError(e?.message || "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  }

  async function handleClick(item: RecommendationItem, dwellMs: number) {
    if (!impressionId) return;
    await logClick({
      impression_id: impressionId,
      item_id: item.item_id,
      position: item.position,
      dwell_ms: dwellMs,
      open_type: "modal_read",
    });
  }

  // initial load
  useEffect(() => {
    loadFeed();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load saved IDs from localStorage whenever data changes
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) {
        setSavedIds(new Set());
        return;
      }
      const parsed = JSON.parse(raw);
      const ids = Object.keys(parsed?.saved || {});
      setSavedIds(new Set(ids));
    } catch {
      setSavedIds(new Set());
    }
  }, [data]);

  // REAL “Because you clicked” logic
  useEffect(() => {
    (async () => {
      try {
        const r = await getRecentClicks(anonId, 10);
        if (!r.recent_clicks.length) {
          setBecauseData(null);
          return;
        }

        const res = await getRecommendations({
          anonymous_id: anonId,
          session_id: sessionId,
          device_type: "web",
          app_version: "nextjs",
          user_agent: "recsys-frontend",
          referrer: "because_you_clicked",
          page_size: 12,
          surface: "because_you_clicked",
          locale: "en-US",
        });

        setBecauseData(res);
      } catch {
        setBecauseData(null);
      }
    })();
  }, [anonId, sessionId]);

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      {/* Top bar */}
      <div className="sticky top-0 z-40 border-b border-white/10 bg-zinc-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="text-xl font-black tracking-tight">NewsFlix</div>
              <div className="text-xs text-white/60">Netflix-style UI for your FastAPI recommender</div>
            </div>

            {/* Nav */}
            <nav className="ml-2 flex items-center gap-4 text-sm text-white/80">
              <Link href="/" className="hover:text-white">
                Home
              </Link>
              <Link href="/dashboard" className="hover:text-white">
                  Dashboard
                </Link>

              <Link href="/profile" className="hover:text-white">
                Profile
              </Link>
              <Link href="/settings" className="hover:text-white">
                Settings
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search titles..."
              className="w-[260px] rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm outline-none placeholder:text-white/40 focus:border-white/30"
            />

            <button
              onClick={() => setDevMode((v) => !v)}
              className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm hover:bg-white/10"
              title="Toggle developer mode (show scores + impression id)"
            >
              {devMode ? "Dev Mode: ON" : "Dev Mode: OFF"}
            </button>

            <button
              onClick={loadFeed}
              className="rounded-2xl bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-white/90"
              disabled={loading}
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-6xl px-4 pb-16">
        {/* Hero */}
        <section className="mt-8 rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 to-white/5 p-7">
          <div className="flex flex-col gap-3">
            {devMode && (
              <div className="text-xs text-white/60">
                impression: <span className="font-mono">{impressionId || "—"}</span> • anon:{" "}
                <span className="font-mono">{anonId}</span>
              </div>
            )}

            <h1 className="text-3xl font-extrabold leading-tight">
              {hero ? hero.title : "Your personalized feed"}
            </h1>

            <p className="max-w-2xl text-sm text-white/70">
              Click any card to open the article modal. Press “Read” to log a click event to your backend.
            </p>

            <div className="mt-2 flex flex-wrap gap-3">
              <button
                onClick={() => {
                  setSessionId(uuid());
                  setData(null);
                  loadFeed();
                }}
                className="rounded-2xl border border-white/10 px-4 py-2 text-sm hover:bg-white/10"
              >
                New session
              </button>

              <button
                onClick={() => {
                  const nu = `anon_${Math.random().toString(16).slice(2, 8)}`;
                  setAnonId(nu);
                  setData(null);
                  loadFeed();
                }}
                className="rounded-2xl border border-white/10 px-4 py-2 text-sm hover:bg-white/10"
              >
                New user
              </button>
            </div>

            {error && (
              <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                {error}
              </div>
            )}
          </div>
        </section>

        {/* Saved row */}
        {savedItems.length > 0 && (
          <Row
            title="Saved for later"
            items={savedItems}
            devMode={devMode}
            onOpen={(it) => {
              setSelected(it);
              setModalOpen(true);
            }}
          />
        )}

        {/* REAL Because-you-clicked row */}
        {becauseItems.length > 0 && (
          <Row
            title="Because you clicked"
            items={becauseItems}
            devMode={devMode}
            onOpen={(it) => {
              setSelected(it);
              setModalOpen(true);
            }}
          />
        )}

        <Row
          title="For You"
          items={row1}
          devMode={devMode}
          onOpen={(it) => {
            setSelected(it);
            setModalOpen(true);
          }}
        />
        <Row
          title="Trending Now"
          items={row2.length ? row2 : row1}
          devMode={devMode}
          onOpen={(it) => {
            setSelected(it);
            setModalOpen(true);
          }}
        />
      </div>

      <ArticleModal
        open={modalOpen}
        item={selected}
        impressionId={impressionId}
        onClose={() => setModalOpen(false)}
        onClick={handleClick}
      />
    </main>
  );
}
