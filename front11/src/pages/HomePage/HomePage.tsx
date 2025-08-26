// front11/src/pages/HomePage/HomePage.tsx

import React, { useState } from "react";
import AddOrCreateInvoiceModal from "../../components/AddOrCreateInvoiceModal";
import ScanVinModal from "../../components/ScanVinModal";
import VinResultsModal from "../../components/VinResultsModal";
import CustomerSelectModal from "../../components/CustomerSelectModal";
import ChangePasswordModal from "../../components/ChangePasswordModal";
import { VehicleResponse } from "../../types";
import { useNavigate } from "react-router-dom";

const HomePage: React.FC = () => {
  const [showAddInvoice, setShowAddInvoice] = useState(false);
  const [showScanVin, setShowScanVin] = useState(false);
  const [showCustomerSelect, setShowCustomerSelect] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [customerID, setCustomerID] = useState<string | null>(null);
  const [vinResult, setVinResult] = useState<VehicleResponse | null>(null);
  const [showVinResultsModal, setShowVinResultsModal] = useState(false);
  const [lastSix, setLastSix] = useState<string | null>(null);
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div>
        <button onClick={() => setShowAddInvoice(true)}>
          Add or Create Invoice
        </button>
        <button onClick={() => navigate("/invoice")}>
          Review & Send Invoice
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
      {showScanVin && (
        <ScanVinModal
          onClose={() => setShowScanVin(false)}
          setVinResult={setVinResult}
          setLastSix={setLastSix}
          openResultsModal={() => setShowVinResultsModal(true)}
        />
      )}

      {showVinResultsModal && vinResult && (
        <VinResultsModal
          vinData={vinResult}
          isOpen={showVinResultsModal}
          onClose={() => setShowVinResultsModal(false)}
        />
      )}
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
