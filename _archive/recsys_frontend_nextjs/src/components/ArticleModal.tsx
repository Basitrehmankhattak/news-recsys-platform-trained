"use client";

import { useMemo, useState } from "react";
import type { RecommendationItem } from "@/lib/api";

type Props = {
  open: boolean;
  item: RecommendationItem | null;
  impressionId: string | null;
  onClose: () => void;
  onClick: (item: RecommendationItem, dwellMs: number) => Promise<void>;
};

export default function ArticleModal({ open, item, impressionId, onClose, onClick }: Props) {
  const [loading, setLoading] = useState(false);
  const openedAt = useMemo(() => Date.now(), [open]);

  if (!open || !item) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm">
      <div className="mx-auto mt-10 w-[92%] max-w-3xl rounded-3xl border border-white/10 bg-zinc-950 p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-6">
          <div>
            <div className="text-xs text-white/60 mb-2">
              impression: <span className="font-mono">{impressionId || "unknown"}</span>
            </div>
            <h3 className="text-2xl font-bold leading-tight">{item.title}</h3>
            <div className="mt-2 text-xs text-white/50 font-mono">{item.item_id}</div>
          </div>

          <button
            onClick={onClose}
            className="rounded-xl border border-white/10 px-3 py-2 text-sm hover:bg-white/10"
          >
            ✕
          </button>
        </div>

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4 text-white/70">
          <p className="text-sm leading-relaxed">
            This is a demo “article page” (your backend currently returns title only).
            In a full product, we’d fetch full content by <span className="font-mono">item_id</span>.
          </p>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            disabled={loading}
            onClick={async () => {
              if (!item) return;
              setLoading(true);
              const dwellMs = Math.max(0, Date.now() - openedAt);
              try {
                await onClick(item, dwellMs);
              } finally {
                setLoading(false);
              }
            }}
            className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-black hover:bg-white/90 disabled:opacity-60"
          >
            {loading ? "Logging..." : "▶ Read (log click)"}
          </button>

          <button
            onClick={onClose}
            className="rounded-2xl border border-white/10 px-5 py-3 text-sm hover:bg-white/10"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
