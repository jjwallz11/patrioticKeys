// front11/src/pages/HomePage/HomePage.tsx

import React, { useState } from "react";
import ScanVinModal from "../../components/ScanVinModal";
import VinResultsModal from "../../components/VinResultsModal";
import CustomerSelectModal from "../../components/CustomerSelectModal";
import ChangePasswordModal from "../../components/ChangePasswordModal";
import { VehicleResponse } from "../../types";
import { useNavigate } from "react-router-dom";
import "../../components/ScanVinModal/ScanVinModal.css";
import "../../components/BaseModal/BaseModal.css";

const HomePage: React.FC = () => {
  const [showScanVin, setShowScanVin] = useState(false);
  const [showCustomerSelect, setShowCustomerSelect] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [vinResult, setVinResult] = useState<VehicleResponse | null>(null);
  const [showVinResultsModal, setShowVinResultsModal] = useState(false);
  const [lastSix, setLastSix] = useState<string | null>(null);
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div>
        <button
          onClick={() =>
            navigate("/invoice", {
              state: { selectedCustomer, vehicle: vinResult },
            })
          }
          disabled={!selectedCustomer}
        >
          Review & Send Invoice
        </button>
        <button onClick={() => setShowScanVin(true)} disabled={!selectedCustomer}>
          Scan VIN
        </button>
        <button onClick={() => setShowCustomerSelect(true)}>
          Select Customer
        </button>
        <button onClick={() => setShowChangePassword(true)}>
          Change Password
        </button>
      </div>

      {selectedCustomer && (
        <p>
          Selected Customer: {selectedCustomer.name} (ID: {selectedCustomer.id})
        </p>
      )}

      {showScanVin && (
        <ScanVinModal
          onClose={() => setShowScanVin(false)}
          setVinResult={setVinResult}
          setLastSix={setLastSix}
          openResultsModal={() => setShowVinResultsModal(true)}
        />
      )}

      {showVinResultsModal && vinResult && selectedCustomer && (
        <VinResultsModal
          vinData={vinResult}
          customerId={selectedCustomer.id}
          isOpen={showVinResultsModal}
          onClose={() => setShowVinResultsModal(false)}
        />
      )}

      {showCustomerSelect && (
        <CustomerSelectModal
          onClose={() => setShowCustomerSelect(false)}
          onCustomerSelect={(id, name) => {
            setSelectedCustomer({ id, name });
            setShowScanVin(true);
          }}
          setVinResult={setVinResult}
          setLastSix={setLastSix}
          openResultsModal={() => setShowVinResultsModal(true)}
        />
      )}

      {showChangePassword && (
        <ChangePasswordModal onClose={() => setShowChangePassword(false)} />
      )}
    </div>
  );
};

export default HomePage;