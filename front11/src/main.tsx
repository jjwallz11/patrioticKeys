// front11/src/main.tsx

import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import { ModalProvider } from "./context/Modal";
import { AuthProvider } from "./context/Auth";
import './index.css';

if (
  import.meta.env.MODE === "production" &&
  import.meta.env.VITE_API_BASE_URL
) {
  const base = String(import.meta.env.VITE_API_BASE_URL).replace(/\/$/, "");
  const nativeFetch = window.fetch.bind(window);

  window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
    if (typeof input === "string" && input.startsWith("/api")) {
      return nativeFetch(base + input, init);
    }
    if (input instanceof URL && input.pathname.startsWith("/api")) {
      const url = base + input.pathname + input.search + input.hash;
      return nativeFetch(url, init);
    }
    return nativeFetch(input as any, init);
  };
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <ModalProvider>
        <RouterProvider router={router} />
      </ModalProvider>
    </AuthProvider>
  </React.StrictMode>
);
