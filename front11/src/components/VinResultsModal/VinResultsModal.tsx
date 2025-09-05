// front11/src/components/VinResultsModal/VinResultsModal.tsx

import React, { useEffect, useState } from "react";
import { VehicleResponse } from "../../types";
import csrfFetch from "../../utils/csrf";
import AddToInvoiceModal from "../AddToInvoiceModal/AddToInvoiceModal";
import CreateInvoiceModal from "../CreateInvoiceModal/CreateInvoiceModal";

interface VinResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  vinData: VehicleResponse | null;
  customerId: string;
}

const VinResultsModal: React.FC<VinResultsModalProps> = ({
  isOpen,
  onClose,
  vinData,
  customerId,
}) => {
  const [invoiceId, setInvoiceId] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddToInvoice, setShowAddToInvoice] = useState(false);
  const [showCreateInvoice, setShowCreateInvoice] = useState(false);

  useEffect(() => {
    const checkInvoice = async () => {
      setChecking(true);
      setError(null);
      try {
        const res = await csrfFetch(
          `/api/qb/customers/${customerId}/invoices/today`
        );
        if (res.ok) {
          const data = await res.json();
          setInvoiceId(data.Id);
        } else {
          setInvoiceId(null);
        }
      } catch (err: any) {
        setError("Could not check for invoice.");
      } finally {
        setChecking(false);
      }
    };

    if (isOpen && vinData && customerId) {
      checkInvoice();
    }
  }, [isOpen, vinData, customerId]);

  if (!isOpen || !vinData) return null;

  const handleStartInvoice = () => {
    setShowCreateInvoice(true);
  };

  const handleAddToInvoice = () => {
    setShowAddToInvoice(true);
  };

  return (
    <>
      <div className="modal-overlay">
        <div className="modal-container">
          <h2 className="modal-title">Vehicle Details</h2>
          <div className="modal-content">
            <p>
              <strong>VIN:</strong> {vinData.vin}
            </p>
            <p>
              <strong>Make:</strong> {vinData.make || "N/A"}
            </p>
            <p>
              <strong>Model:</strong> {vinData.model || "N/A"}
            </p>
            <p>
              <strong>Year:</strong> {vinData.year || "N/A"}
            </p>
            <p>
              <strong>Body Type:</strong> {vinData.bodyType || "N/A"}
            </p>
            <p>
              <strong>Fuel Type:</strong> {vinData.fuelType || "N/A"}
            </p>
            <p>
              <strong>Manufacturer:</strong> {vinData.manufacturer || "N/A"}
            </p>
            <p>
              <strong>Plant Country:</strong> {vinData.plantCountry || "N/A"}
            </p>
          </div>

          {checking ? (
            <p>Checking for invoice...</p>
          ) : error ? (
            <p className="error-text">{error}</p>
          ) : invoiceId ? (
            <button className="btn-edit" onClick={handleAddToInvoice}>
              Add to Invoice
            </button>
          ) : (
            <button className="btn-edit" onClick={handleStartInvoice}>
              Create Invoice
            </button>
          )}

          <div className="modal-actions">
            <button onClick={onClose} className="btn btn-primary">
              Close
            </button>
          </div>
        </div>
      </div>

      {showCreateInvoice && (
        <CreateInvoiceModal
          customerId={customerId}
          onClose={() => setShowCreateInvoice(false)}
          onInvoiceCreated={(newId) => {
            setInvoiceId(newId); // 👈 update state with real invoice ID
            setShowCreateInvoice(false);
            setShowAddToInvoice(true); // 👈 optionally open AddToInvoiceModal directly
          }}
        />
      )}

      {showAddToInvoice && invoiceId && (
        <AddToInvoiceModal
          vehicle={vinData}
          invoiceId={invoiceId}
          onClose={() => setShowAddToInvoice(false)}
        />
      )}
    </>
  );
};

export default VinResultsModal;
