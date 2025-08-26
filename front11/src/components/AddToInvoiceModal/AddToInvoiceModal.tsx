// front11/src/components/AddToInvoiceModal/AddToInvoiceModal.tsx

import React, { useState } from "react";
import BaseModal from "../BaseModal/BaseModal";
import ItemSelectModal from "../ItemSelectModal/ItemSelectModal";
import csrfFetch from "../../utils/csrf";
import { VehicleResponse } from "../../types";

interface AddToInvoiceModalProps {
  vehicle: VehicleResponse;
  invoiceId: string;
  onClose: () => void;
  onSuccess?: () => void;
}

const AddToInvoiceModal: React.FC<AddToInvoiceModalProps> = ({
  vehicle,
  invoiceId,
  onClose,
  onSuccess,
}) => {
  const [selectedItem, setSelectedItem] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [showItemSelect, setShowItemSelect] = useState(false);

  const getFormattedDescription = (itemName: string) => {
    return `**${itemName}**\n${vehicle.ModelYear || "Unknown"} ${
      vehicle.Make || "Unknown"
    } ${vehicle.Model || "Unknown"} (…${vehicle.VIN?.slice(-6) || "XXXXXX"})`;
  };

  const [description, setDescription] = useState("");

  const handleSubmit = async () => {
    if (!selectedItem) {
      alert("Please select an item.");
      return;
    }

    try {
      const res = await csrfFetch("/api/invoices/items", {
        method: "POST",
        body: JSON.stringify({
          vin: vehicle.VIN,
          invoice_id: invoiceId,
          item_id: selectedItem.id,
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
        <p>
          <strong>VIN:</strong> {vehicle.VIN}
        </p>

        <button className="btn-edit" onClick={() => setShowItemSelect(true)}>
          {selectedItem ? "Change Item" : "Select Item"}
        </button>

        {selectedItem && (
          <p style={{ marginTop: "0.5rem" }}>
            Selected Item ID: <code>{selectedItem.id}</code>
          </p>
        )}

        <textarea
          placeholder="Optional Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={5}
        />
      </BaseModal>

      {showItemSelect && (
        <ItemSelectModal
          onClose={() => setShowItemSelect(false)}
          onItemSelect={(item) => {
            setSelectedItem(item);
            setDescription(getFormattedDescription(item.name));
            setShowItemSelect(false);
          }}
        />
      )}
    </>
  );
};

export default AddToInvoiceModal;
