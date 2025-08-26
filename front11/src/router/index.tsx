// src/router/index.tsx

import { createBrowserRouter } from "react-router-dom";
import Layout from "./Layout";
import LoginPage from "../pages/LoginPage";
import HomePage from "../pages/HomePage";
import InvoicePage from "../pages/InvoicePage";

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <LoginPage />,
      },
      {
        path: "/home",
        element: <HomePage />,
      },
      {
        path: "/invoice",
        element: <InvoicePage />,
      },
    ],
  },
]);
