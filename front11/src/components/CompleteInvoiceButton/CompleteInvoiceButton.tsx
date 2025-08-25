// front11/src/components/CompleteInvoiceButton/CompleteInvoiceButton.tsx

import { useState } from "react";
import ConfirmationModal from "../ConfirmationModal/ConfirmationModal";
import csrfFetch from "../../utils/csrf";

const CompleteInvoiceButton = () => {
  const [showModal, setShowModal] = useState(false);

  const handleCompleteInvoice = async () => {
    try {
      const res = await csrfFetch("/api/invoices/send", {
        method: "POST",
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to send invoice.");
      }

      const data = await res.json();
      alert(`Invoice ${data.invoice_number} sent to ${data.customer}.`);

      await csrfFetch("/api/reset-customer", { method: "POST" });
    } catch (err: any) {
      alert(err.message || "Something went wrong.");
    } finally {
      setShowModal(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="confirm-btn"
      >
        Complete Invoice
      </button>

      {showModal && (
        <ConfirmationModal
          title="Send Invoice?"
          message="This will send the full invoice to the selected customer and clear your current session."
          onConfirm={handleCompleteInvoice}
          onCancel={() => setShowModal(false)}
        />
      )}
    </>
  );
};

export default CompleteInvoiceButton;