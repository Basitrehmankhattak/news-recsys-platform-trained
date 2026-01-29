"use client";

import { useEffect, useMemo, useState } from "react";
import type { RecommendationItem } from "@/lib/api";

type RowProps = {
  title: string;
  items: RecommendationItem[];
  onOpen?: (item: RecommendationItem) => void;
  devMode?: boolean;
};

type Prefs = {
  liked: Record<string, true>;
  saved: Record<string, true>;
  hidden: Record<string, true>;
};

const LS_KEY = "newsflix_prefs_v1";

export default function Row({ title, items, onOpen, devMode = false }: RowProps) {
  const [prefs, setPrefs] = useState<Prefs>({ liked: {}, saved: {}, hidden: {} });

  // Load prefs once
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as Prefs;
      if (parsed?.liked && parsed?.saved && parsed?.hidden) setPrefs(parsed);
    } catch {
      // ignore
    }
  }, []);

  // Persist prefs
  useEffect(() => {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(prefs));
    } catch {
      // ignore
    }
  }, [prefs]);

  const visibleItems = useMemo(() => {
    return items.filter((it) => !prefs.hidden[it.item_id]);
  }, [items, prefs.hidden]);

  function toggle(kind: "liked" | "saved", itemId: string) {
    setPrefs((p) => {
      const next = { ...p, [kind]: { ...p[kind] } } as Prefs;
      if (next[kind][itemId]) delete next[kind][itemId];
      else next[kind][itemId] = true;
      return next;
    });
  }

  function hide(itemId: string) {
    setPrefs((p) => ({ ...p, hidden: { ...p.hidden, [itemId]: true } }));
  }

  function unhideAll() {
    setPrefs((p) => ({ ...p, hidden: {} }));
  }

  return (
    <section className="mt-8">
      <div className="mb-3 flex items-baseline justify-between gap-4">
        <h2 className="text-lg font-bold">{title}</h2>

        <div className="flex items-center gap-3 text-xs text-white/60">
          <span>{visibleItems.length} items</span>

          {Object.keys(prefs.hidden).length > 0 && (
            <button
              onClick={unhideAll}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 hover:bg-white/10"
            >
              Unhide all
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-3">
        {visibleItems.map((it) => {
          const liked = !!prefs.liked[it.item_id];
          const saved = !!prefs.saved[it.item_id];

          return (
            <div
              key={`${it.item_id}-${it.position}`}
              className="group min-w-[240px] max-w-[240px] rounded-2xl border border-white/10 bg-white/5 p-4 hover:bg-white/10"
            >
              {/* Title area clickable */}
              <button onClick={() => onOpen?.(it)} className="text-left w-full">
                <div className="text-sm font-semibold leading-snug line-clamp-3">
                  {it.title || "Untitled"}
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] text-white/50">
                  <span className="font-mono">{it.item_id}</span>
                  <span>#{it.position}</span>
                </div>

                {devMode && (
                  <div className="mt-3 space-y-1 text-[11px] text-white/60 font-mono">
                    <div>retrieval: {fmt(it.retrieval_score, 4)}</div>
                    <div>rank: {fmt(it.rank_score, 6)}</div>
                    <div>final: {fmt(it.final_score, 6)}</div>
                  </div>
                )}
              </button>

              {/* Actions */}
              <div className="mt-3 flex items-center justify-between gap-2">
                <div className="flex gap-2">
                  <button
                    onClick={() => toggle("liked", it.item_id)}
                    className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-xs hover:bg-white/10"
                    title="Like"
                  >
                    {liked ? "❤️ Liked" : "🤍 Like"}
                  </button>

                  <button
                    onClick={() => toggle("saved", it.item_id)}
                    className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-xs hover:bg-white/10"
                    title="Save"
                  >
                    {saved ? "⭐ Saved" : "☆ Save"}
                  </button>
                </div>

                <button
                  onClick={() => hide(it.item_id)}
                  className="rounded-xl border border-white/10 bg-white/5 px-3 py-1 text-xs hover:bg-white/10"
                  title="Hide"
                >
                  🚫 Hide
                </button>
              </div>

              <div className="mt-2 text-[11px] text-white/60 opacity-0 transition group-hover:opacity-100">
                Click title to open
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function fmt(v: unknown, digits: number) {
  if (v === null || v === undefined) return "—";
  const n = typeof v === "number" ? v : Number(v);
  if (Number.isFinite(n)) return n.toFixed(digits);
  return String(v);
}
