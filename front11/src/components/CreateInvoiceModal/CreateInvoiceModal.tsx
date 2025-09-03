// front11/src/components/CreateInvoiceModal/CreateInvoiceModal.tsx

import { useState } from "react";
import csrfFetch from "../../utils/csrf";
import BaseModal from "../BaseModal/BaseModal";

interface CreateInvoiceModalProps {
  customerId: string;
  onClose: () => void;
  onInvoiceCreated: (invoiceId: string) => void;
}

const CreateInvoiceModal = ({
  customerId,
  onClose,
  onInvoiceCreated,
}: CreateInvoiceModalProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateInvoice = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await csrfFetch(
        `/api/qb/customers/${customerId}/invoices/today`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to start invoice");
      }

      const data = await response.json();
      const invoiceId = data?.Id || data?.Invoice?.Id;

      if (!invoiceId) {
        throw new Error("Invoice ID missing from response");
      }

      onInvoiceCreated(invoiceId);
      onClose();
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    }
  };

  return (
    <BaseModal title="Start Today's Invoice" onClose={onClose}>
      <div className="createinvoice-modal__body">
        <p>Do you want to start today's invoice for this customer?</p>
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

export default CreateInvoiceModal;
