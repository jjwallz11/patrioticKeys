// front11/src/components/CustomerSelectModal/CustomerSelectModal.tsx

import { useState, useEffect } from "react";
import BaseModal from "../BaseModal/BaseModal";
import AddCustomerModal from "../AddCustomerModal/AddCustomerModal";
import csrfFetch from "../../utils/csrf";

interface Customer {
  id: string;
  name: string;
  email: string;
}

interface CustomerSelectModalProps {
  onClose: () => void;
  onCustomerSelect: (customerId: string) => void;
}

const CustomerSelectModal = ({
  onClose,
  onCustomerSelect,
}: CustomerSelectModalProps) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddCustomer, setShowAddCustomer] = useState(false);

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const res = await csrfFetch("/api/qb/customers", { credentials: "include" });
        if (!res.ok) throw new Error("Failed to load customers");
        const data = await res.json();
        setCustomers(data.customers || []);
      } catch (err: any) {
        setError(err.message || "Error loading customers");
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, [showAddCustomer]);

  const handleSelect = (id: string) => {
    onCustomerSelect(id);
    onClose();
  };

  return (
    <>
      <BaseModal title="Select a Customer" onClose={onClose}>
        <div className="customer-select-modal__body">
          {loading && <p>Loading customers...</p>}
          {error && <p className="error-text">{error}</p>}
          {!loading && !error && customers.length === 0 && (
            <p>No customers yet.</p>
          )}

          <ul className="customer-list">
            {customers.map((customer) => (
              <li key={customer.id}>
                <button
                  className="btn-edit"
                  onClick={() => handleSelect(customer.id)}
                >
                  {customer.name}
                </button>
              </li>
            ))}
          </ul>

          <div className="base-modal__actions">
            <button
              className="btn-edit"
              onClick={() => setShowAddCustomer(true)}
            >
              Add New Customer
            </button>
            <button className="btn-delete" onClick={onClose}>
              Cancel
            </button>
          </div>
        </div>
      </BaseModal>

      {showAddCustomer && (
        <AddCustomerModal onClose={() => setShowAddCustomer(false)} />
      )}
    </>
  );
};

export default CustomerSelectModal;
