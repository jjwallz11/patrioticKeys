// front11/src/components/AddCustomerModal/AddCustomerModal.tsx

import React, { useState } from "react";
import BaseModal from "../BaseModal/BaseModal";
import csrfFetch from "../../utils/csrf";

interface AddCustomerModalProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const AddCustomerModal: React.FC<AddCustomerModalProps> = ({ onClose, onSuccess }) => {
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const handleSubmit = async () => {
    if (!displayName.trim()) {
      alert("Display name is required.");
      return;
    }

    try {
      const res = await csrfFetch("/api/customers", {
        method: "POST",
        body: JSON.stringify({ display_name: displayName, email, phone }),
      });

      if (!res.ok) {
        throw new Error("Failed to add customer");
      }

      onSuccess?.();
      onClose();
    } catch (err) {
      console.error(err);
      alert("Error creating customer. Please try again.");
    }
  };

  return (
    <BaseModal title="Add New Customer" onClose={onClose} onSave={handleSubmit}>
      <input
        type="text"
        placeholder="Display Name *"
        value={displayName}
        onChange={(e) => setDisplayName(e.target.value)}
      />
      <input
        type="email"
        placeholder="Email (optional)"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="tel"
        placeholder="Phone (optional)"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />
    </BaseModal>
  );
};

export default AddCustomerModal;