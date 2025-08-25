// front11/src/utils/csrf.ts

const csrfFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const res = await fetch("/api/csrf/token");
  if (!res.ok) throw new Error("Failed to fetch CSRF token");

  const data = await res.json();
  const csrfToken = data.csrfToken;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    "csrf-token": csrfToken,
    ...options.headers,
  };

  return fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });
};

export default csrfFetch;