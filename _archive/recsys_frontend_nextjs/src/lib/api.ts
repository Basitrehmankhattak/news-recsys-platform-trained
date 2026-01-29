export type RecommendationRequest = {
  anonymous_id: string;
  session_id: string;
  device_type?: string;
  app_version?: string;
  user_agent?: string;
  referrer?: string;
  page_size?: number;
  surface?: string;
  locale?: string;
};

export type RecommendationItem = {
  item_id: string;
  title: string;
  position: number;
  retrieval_score?: number;
  rank_score?: number;
  final_score?: number;
  retrieval_pos?: number;
};

export type RecommendationResponse = {
  impression_id: string;
  items: RecommendationItem[];
};

export type ClickRequest = {
  impression_id: string;
  item_id: string;
  position: number;
  dwell_ms: number;
  open_type: string;
};

export type RecentClicksResponse = {
  anonymous_id: string;
  recent_clicks: string[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function parseError(res: Response) {
  const text = await res.text().catch(() => "");
  return `HTTP ${res.status} ${res.statusText}${text ? ` — ${text}` : ""}`;
}

export async function getRecommendations(payload: RecommendationRequest): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function logClick(payload: ClickRequest): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/click`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getRecentClicks(anonymous_id: string, limit = 10): Promise<RecentClicksResponse> {
  const url = `${API_BASE}/users/${encodeURIComponent(anonymous_id)}/recent_clicks?limit=${limit}`;

  const res = await fetch(url, { method: "GET" });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}
