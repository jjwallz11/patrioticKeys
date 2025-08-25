// front11/src/pages/HomePage/HomePage.tsx

import React, { useState } from "react";
import AddOrCreateInvoiceModal from "../../components/AddOrCreateInvoiceModal";
import ScanVinModal from "../../components/ScanVinModal";
import CustomerSelectModal from "../../components/CustomerSelectModal";
import ChangePasswordModal from "../../components/ChangePasswordModal";

const HomePage: React.FC = () => {
  const [showAddInvoice, setShowAddInvoice] = useState(false);
  const [showScanVin, setShowScanVin] = useState(false);
  const [showCustomerSelect, setShowCustomerSelect] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [customerID, setCustomerID] = useState<string | null>(null);

  return (
    <div className="home-page" style={{ padding: "2rem", textAlign: "center" }}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
          marginTop: "2rem",
        }}
      >
        <button onClick={() => setShowAddInvoice(true)}>
          Add or Create Invoice
        </button>
        <button onClick={() => setShowScanVin(true)}>Scan VIN</button>
        <button onClick={() => setShowCustomerSelect(true)}>
          Select Customer
        </button>
        <button onClick={() => setShowChangePassword(true)}>
          Change Password
        </button>
      </div>

      {showAddInvoice && customerID && (
        <AddOrCreateInvoiceModal
          customerId={customerID}
          onClose={() => setShowAddInvoice(false)}
        />
      )}
      {showScanVin && <ScanVinModal onClose={() => setShowScanVin(false)} />}
      {showCustomerSelect && (
        <CustomerSelectModal
          onClose={() => setShowCustomerSelect(false)}
          onCustomerSelect={(id) => setCustomerID(id)}
        />
      )}
      {showChangePassword && (
        <ChangePasswordModal onClose={() => setShowChangePassword(false)} />
      )}
    </div>
  );
};

export default HomePage;
