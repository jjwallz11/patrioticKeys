// front11/src/components/AddToInvoiceModal/AddToInvoiceModal.tsx

import React, { useState } from "react";
import BaseModal from "../BaseModal/BaseModal";
import ItemSelectModal from "../ItemSelectModal/ItemSelectModal";
import csrfFetch from "../../utils/csrf";
import { VehicleResponse } from "../../types";

interface AddToInvoiceModalProps {
  vehicle: VehicleResponse;
  invoiceId?: string; // <-- made optional
  customerId: string; // <-- added
  onClose: () => void;
  onSuccess?: (newInvoiceId?: string) => void;
}

const AddToInvoiceModal: React.FC<AddToInvoiceModalProps> = ({
  vehicle,
  invoiceId,
  customerId,
  onClose,
  onSuccess,
}) => {
  const [selectedItem, setSelectedItem] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [showItemSelect, setShowItemSelect] = useState(false);
  const [description, setDescription] = useState("");
  const [rate, setRate] = useState<number>(0);
  const [qty, setQty] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getFormattedDescription = (itemName: string) => {
    return `**${itemName}**\n${vehicle.year || "Unknown"} ${
      vehicle.make || "Unknown"
    } ${vehicle.model || "Unknown"} (…${vehicle.vin?.slice(-6) || "XXXXXX"})`;
  };

  const handleSubmit = async () => {
    if (!selectedItem) {
      alert("Please select an item.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let res;

      if (invoiceId) {
        // 🔁 Add to existing invoice
        res = await csrfFetch("/api/invoices/items", {
          method: "POST",
          body: JSON.stringify({
            vin: vehicle.vin,
            invoice_id: invoiceId,
            item_name: selectedItem.name,
            description,
            rate,
            qty,
          }),
        });

        if (!res.ok) throw new Error("Failed to add item to invoice");
        onSuccess?.();
        onClose();
      } else {
        // 🆕 Create new invoice with line item
        res = await csrfFetch(`/api/qb/customers/${customerId}/invoices/today`, {
          method: "POST",
          body: JSON.stringify({
            item_id: selectedItem.id,
            description,
            rate,
            qty,
          }),
        });

        const data = await res.json();
        if (!res.ok || !data?.Id) throw new Error(data?.detail || "Invoice creation failed");

        onSuccess?.(data.Id);
        onClose();
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <BaseModal
        title={invoiceId ? "Add Line Item" : "Create Invoice"}
        onClose={onClose}
        onSave={handleSubmit}
      >
        {error && <p className="error-text">{error}</p>}

        <p>
          <strong>VIN:</strong> {vehicle.vin}
        </p>

        <button className="btn-edit" onClick={() => setShowItemSelect(true)}>
          {selectedItem ? "Change Item" : "Select Item"}
        </button>

        {selectedItem && (
          <p style={{ marginTop: "0.5rem" }}>
            Selected Item & ID: <code>{selectedItem.name};{selectedItem.id}</code>
          </p>
        )}

        <label>Rate ($):</label>
        <input
          type="number"
          value={rate}
          onChange={(e) => setRate(parseFloat(e.target.value))}
        />

        <label>Quantity:</label>
        <input
          type="number"
          value={qty}
          onChange={(e) => setQty(parseInt(e.target.value))}
        />

        <label>Description:</label>
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