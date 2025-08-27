// src/router/layout.tsx

import { Outlet } from "react-router-dom";
import "./Layout.css";

const Layout = () => {
  return (
    <div className="app-layout">
      <img src="/pkLogo.png" alt="Patriotic Keys Logo" className="pk-logo"/>
      {/* <header className="app-header">Patriotic Keys</header> */}
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;