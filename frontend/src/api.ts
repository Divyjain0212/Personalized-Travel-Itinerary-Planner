declare global {
  interface ImportMeta {
    readonly env?: {
      readonly VITE_API_URL?: string;
    };
  }
}

export type Preferences = {
  destination: string; vibe: string; duration_days: number; travel_dates: string[];
  budget: string; travel_party: string; pace: string; interests: string[]; group_size: number;
};
export type AIConfig = { provider: "demo" | "gemini" | "groq"; api_key: string };
export type Slot = { time: string; title: string; description: string; cost_local: number; cost_usd: number; cost_inr: number; category: string };
export type Day = { day_number: number; area: string; route_summary: string; slots: Slot[]; daily_cost_local: number; cumulative_cost_local: number };
export type Itinerary = { title: string; destination: string; currency: string; usd_rate: number; days: Day[]; total_cost_local: number; total_cost_usd: number; total_cost_inr: number };
export type Recommendation = { city: string; country: string; match_score: number; reason: string; tags: string[] };
export type PlanResponse = { preferences: Preferences; recommendations: Recommendation[]; itinerary: Itinerary | null };
export type SavedTrip = { id: string; name: string; destination: string; duration_days: number; budget: string; saved_at: string; preferences: Preferences; itinerary: Itinerary };

const API_URL = import.meta.env?.VITE_API_URL ?? "http://localhost:8082";
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  } catch {
    throw new Error(`Cannot reach the planner API at ${API_URL}. Start the FastAPI server with "uvicorn app.main:app --reload --port 8000".`);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}
export const planTrip = (preferences: Preferences, ai: AIConfig) => request<PlanResponse>("/api/itineraries/generate", { method: "POST", body: JSON.stringify({ preferences, ai }) });
export const swapActivity = (body: { preferences: Preferences; ai: AIConfig; itinerary: Itinerary; day_number: number; slot_index: number; request: string }) => request<PlanResponse>("/api/itineraries/swap", { method: "POST", body: JSON.stringify(body) });
export const saveTrip = (body: { name: string; preferences: Preferences; itinerary: Itinerary }) => request<SavedTrip>("/api/trips", { method: "POST", body: JSON.stringify(body) });
export const getTrips = () => request<SavedTrip[]>("/api/trips");
