// front11/src/utils/csrf.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const csrfFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const tokenRes = await fetch(`${API_BASE_URL}/api/csrf/token`, {
    credentials: "include",
  });
  if (!tokenRes.ok) throw new Error("Failed to fetch CSRF token");

  const data = await tokenRes.json();
  const csrfToken = data.csrfToken;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    "csrf-token": csrfToken,
    ...options.headers,
  };

  return fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
    credentials: "include",
  });
};

export default csrfFetch;