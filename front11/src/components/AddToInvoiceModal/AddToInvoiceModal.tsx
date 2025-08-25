import React, { useState } from "react";
import BaseModal from "../BaseModal/BaseModal";
import ItemSelectModal from "../ItemSelectModal/ItemSelectModal";
import csrfFetch from "../../utils/csrf";

interface AddToInvoiceModalProps {
  vin: string;
  invoiceId: string;
  onClose: () => void;
  onSuccess?: () => void;
}

const AddToInvoiceModal: React.FC<AddToInvoiceModalProps> = ({
  vin,
  invoiceId,
  onClose,
  onSuccess,
}) => {
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [showItemSelect, setShowItemSelect] = useState(false);
  const [description, setDescription] = useState("");

  const handleSubmit = async () => {
    if (!selectedItemId) {
      alert("Please select an item.");
      return;
    }

    try {
      const res = await csrfFetch("/api/invoices/items", {
        method: "POST",
        body: JSON.stringify({
          vin,
          invoice_id: invoiceId,
          item_id: selectedItemId,
          description,
        }),
      });

      if (!res.ok) throw new Error("Failed to add item to invoice");

      onSuccess?.();
      onClose();
    } catch (err) {
      console.error(err);
      alert("Error adding item to invoice.");
    }
  };

  return (
    <>
      <BaseModal title="Add Line Item" onClose={onClose} onSave={handleSubmit}>
        <p><strong>VIN:</strong> {vin}</p>

        <button className="btn-edit" onClick={() => setShowItemSelect(true)}>
          {selectedItemId ? "Change Item" : "Select Item"}
        </button>

        {selectedItemId && (
          <p style={{ marginTop: "0.5rem" }}>
            Selected Item ID: <code>{selectedItemId}</code>
          </p>
        )}

        <textarea
          placeholder="Optional Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </BaseModal>

      {showItemSelect && (
        <ItemSelectModal
          onClose={() => setShowItemSelect(false)}
          onItemSelect={(id) => {
            setSelectedItemId(id);
            setShowItemSelect(false);
          }}
        />
      )}
    </>
  );
};

export default AddToInvoiceModal;