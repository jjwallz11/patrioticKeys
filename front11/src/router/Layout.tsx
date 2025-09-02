// src/router/layout.tsx

import { Outlet } from "react-router-dom";
import "./Layout.css";

const Layout = () => {
  return (
    <div className="app-layout">
      <img
        src={`${import.meta.env.BASE_URL}pkLogo.png?v=2`}
        alt="Patriotic Keys Logo"
        className="pk-logo"
        style={{ cursor: "pointer" }}
        onClick={() => (window.location.href = "/home")}
      />
      {/* <header className="app-header">Patriotic Keys</header> */}
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
