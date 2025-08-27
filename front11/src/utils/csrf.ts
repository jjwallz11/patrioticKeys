// front11/src/utils/csrf.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

const csrfFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const csrfToken = getCsrfToken();
  if (!csrfToken) throw new Error("CSRF token not found in cookies");

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