"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import ArticleModal from "@/components/ArticleModal";
import {
  getRecommendations,
  logClick,
  type RecommendationItem,
  type RecommendationResponse,
} from "@/lib/api";

function uuid() {
  return crypto.randomUUID();
}

function splitColumns(items: RecommendationItem[]) {
  // simple deterministic split for now (replace with real status later)
  const pending = items.filter((x) => x.position >= 1 && x.position <= 12);
  const inReview = items.filter((x) => x.position >= 13 && x.position <= 24);
  const approved = items.filter((x) => x.position >= 25 && x.position <= 36);
  return { pending, inReview, approved };
}

function Column({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-w-[320px] flex-1 flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-zinc-900">{title}</div>
        <div className="rounded-full bg-zinc-200 px-2 py-0.5 text-xs text-zinc-700">
          {count}
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-3 rounded-2xl bg-white p-3 shadow-sm ring-1 ring-zinc-200">
        {children}
      </div>
    </div>
  );
}

function Card({
  item,
  devMode,
  onOpen,
}: {
  item: RecommendationItem;
  devMode: boolean;
  onOpen: (it: RecommendationItem) => void;
}) {
  return (
    <button
      onClick={() => onOpen(item)}
      className="w-full rounded-2xl border border-zinc-200 bg-zinc-50 p-4 text-left hover:bg-white"
      title={item.title}
    >
      <div className="line-clamp-2 text-sm font-semibold text-zinc-900">
        {item.title || "Untitled"}
      </div>

      <div className="mt-2 flex items-center justify-between text-[11px] text-zinc-500">
        <span className="font-mono">{item.item_id}</span>
        <span>#{item.position}</span>
      </div>

      {devMode && (
        <div className="mt-3 space-y-1 text-[11px] font-mono text-zinc-600">
          <div>retrieval: {fmt(item.retrieval_score, 4)}</div>
          <div>rank: {fmt(item.rank_score, 6)}</div>
          <div>final: {fmt(item.final_score, 6)}</div>
        </div>
      )}
    </button>
  );
}

function fmt(v: unknown, digits: number) {
  if (v === null || v === undefined) return "—";
  const n = typeof v === "number" ? v : Number(v);
  if (Number.isFinite(n)) return n.toFixed(digits);
  return String(v);
}

export default function DashboardPage() {
  const [anonId, setAnonId] = useState<string>(() => `anon_${Math.random().toString(16).slice(2, 8)}`);
  const [sessionId, setSessionId] = useState<string>(() => uuid());

  const [devMode, setDevMode] = useState(false);
  const [query, setQuery] = useState("");

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState("");

  const [selected, setSelected] = useState<RecommendationItem | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const items = data?.items ?? [];
  const impressionId = data?.impression_id ?? null;

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((x) => (x.title || "").toLowerCase().includes(q));
  }, [items, query]);

  const cols = useMemo(() => splitColumns(filtered), [filtered]);

  async function loadBoard() {
    setLoading(true);
    setError("");
    try {
      const res = await getRecommendations({
        anonymous_id: anonId,
        session_id: sessionId,
        device_type: "web",
        app_version: "nextjs",
        user_agent: "recsys-frontend",
        referrer: "dashboard",
        page_size: 36,
        surface: "editorial_board",
        locale: "en-US",
      });
      setData(res);
    } catch (e: any) {
      setError(e?.message || "Failed to load board");
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

  useEffect(() => {
    loadBoard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main className="min-h-screen bg-zinc-100 text-zinc-900">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="hidden w-64 flex-col bg-zinc-950 text-white md:flex">
          <div className="px-5 py-5">
            <div className="text-lg font-black tracking-tight">NewsBoard</div>
            <div className="mt-1 text-xs text-white/60">
              Editorial-style dashboard
            </div>
          </div>

          <nav className="flex flex-1 flex-col gap-1 px-3">
            <Link className="rounded-xl px-3 py-2 text-sm hover:bg-white/10" href="/dashboard">
              Dashboard
            </Link>
            <Link className="rounded-xl px-3 py-2 text-sm hover:bg-white/10" href="/">
              NewsFlix Feed
            </Link>
            <Link className="rounded-xl px-3 py-2 text-sm hover:bg-white/10" href="/profile">
              Profile
            </Link>
            <Link className="rounded-xl px-3 py-2 text-sm hover:bg-white/10" href="/settings">
              Settings
            </Link>
          </nav>

          <div className="border-t border-white/10 px-5 py-4 text-xs text-white/60">
            {devMode ? (
              <div>
                <div className="font-mono">anon: {anonId}</div>
                <div className="font-mono">impr: {impressionId || "—"}</div>
              </div>
            ) : (
              <div>Toggle Dev Mode to inspect scores</div>
            )}
          </div>
        </aside>

        {/* Main */}
        <div className="flex flex-1 flex-col">
          {/* Top bar */}
          <header className="sticky top-0 z-40 border-b border-zinc-200 bg-white/80 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="text-sm font-semibold text-zinc-900">Dashboard</div>
                <div className="hidden text-xs text-zinc-500 sm:block">
                  Moderation-style board UI (recommendations as cards)
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search news title, author, or tags..."
                  className="w-[320px] rounded-2xl border border-zinc-200 bg-white px-4 py-2 text-sm outline-none placeholder:text-zinc-400 focus:border-zinc-400"
                />

                <button
                  onClick={() => setDevMode((v) => !v)}
                  className="rounded-2xl border border-zinc-200 bg-white px-4 py-2 text-sm hover:bg-zinc-50"
                >
                  {devMode ? "Dev Mode: ON" : "Dev Mode: OFF"}
                </button>

                <button
                  onClick={loadBoard}
                  disabled={loading}
                  className="rounded-2xl bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800 disabled:opacity-60"
                >
                  {loading ? "Loading..." : "Refresh"}
                </button>
              </div>
            </div>
          </header>

          {/* Content */}
          <div className="mx-auto w-full max-w-7xl px-4 py-6">
            {error && (
              <div className="mb-4 rounded-2xl border border-red-300 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="flex gap-4 overflow-x-auto pb-4">
              <Column title="Pending" count={cols.pending.length}>
                {cols.pending.map((it) => (
                  <Card key={it.item_id + it.position} item={it} devMode={devMode} onOpen={(x) => { setSelected(x); setModalOpen(true); }} />
                ))}
              </Column>

              <Column title="In Review" count={cols.inReview.length}>
                {cols.inReview.map((it) => (
                  <Card key={it.item_id + it.position} item={it} devMode={devMode} onOpen={(x) => { setSelected(x); setModalOpen(true); }} />
                ))}
              </Column>

              <Column title="Approved" count={cols.approved.length}>
                {cols.approved.map((it) => (
                  <Card key={it.item_id + it.position} item={it} devMode={devMode} onOpen={(x) => { setSelected(x); setModalOpen(true); }} />
                ))}
              </Column>
            </div>

            {/* quick actions */}
            <div className="mt-4 flex flex-wrap gap-2 text-sm">
              <button
                onClick={() => {
                  setSessionId(uuid());
                  setData(null);
                  loadBoard();
                }}
                className="rounded-2xl border border-zinc-200 bg-white px-4 py-2 hover:bg-zinc-50"
              >
                New session
              </button>

              <button
                onClick={() => {
                  const nu = `anon_${Math.random().toString(16).slice(2, 8)}`;
                  setAnonId(nu);
                  setData(null);
                  loadBoard();
                }}
                className="rounded-2xl border border-zinc-200 bg-white px-4 py-2 hover:bg-zinc-50"
              >
                New user
              </button>
            </div>
          </div>
        </div>
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
