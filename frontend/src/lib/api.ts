// Centralized API base + URL helper for dev/prod
// In dev (Vite), proxy handles /api and /files. In prod, set VITE_API_BASE to your backend URL.
// Example: VITE_API_BASE=https://your-backend.onrender.com

export const API_BASE = (import.meta.env?.VITE_API_BASE || '').replace(/\/$/, '');

// apiUrl builds a full URL for API endpoints and file serving.
// - If API_BASE is set, it prefixes it and strips a leading /api to avoid double /api in prod.
// - If API_BASE is not set (local dev), it returns the path unchanged for the Vite proxy.
export function apiUrl(path: string): string {
  if (!path) return path;
  // Normalize path
  const normalized = path.startsWith('/') ? path : `/${path}`;

  if (!API_BASE) {
    // Dev: let Vite proxy handle /api and /files
    return normalized;
  }

  // Remove leading /api only for API endpoints; keep /files as-is
  const isApi = normalized.startsWith('/api/');
  const cleaned = isApi ? normalized.replace(/^\/api\//, '/') : normalized;

  return `${API_BASE}${cleaned}`;
}