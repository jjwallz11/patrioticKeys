// front11/src/components/AddOrCreateInvoiceModal/AddOrCreateInvoiceModal.tsx

import { useState } from "react";
import csrfFetch from "../../utils/csrf";
import BaseModal from "../BaseModal/BaseModal";

interface AddOrCreateInvoiceModalProps {
  customerId: string;
  onClose: () => void;
}

const AddOrCreateInvoiceModal = ({
  customerId,
  onClose,
}: AddOrCreateInvoiceModalProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateInvoice = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await csrfFetch(
        `/api/customers/${customerId}/invoices/today`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to start invoice");
      }

      console.log("Invoice created or resumed:", data);
      onClose();

      onClose();
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <BaseModal title="Start Today's Invoice" onClose={onClose}>
      <div className="addorcreateinvoice-modal__body">
        <p>Do you want to start or resume today's invoice for this customer?</p>
        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="base-modal__actions">
        <button
          className="btn-edit"
          onClick={handleCreateInvoice}
          disabled={loading}
        >
          {loading ? "Starting..." : "Yes, Start Invoice"}
        </button>
        <button className="btn-delete" onClick={onClose} disabled={loading}>
          Cancel
        </button>
      </div>
    </BaseModal>
  );
};

export default AddOrCreateInvoiceModal;
