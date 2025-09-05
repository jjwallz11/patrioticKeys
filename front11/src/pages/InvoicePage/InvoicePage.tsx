// src/pages/InvoicePage/InvoicePage.tsx

import { useEffect, useState } from "react";
import CompleteInvoiceButton from "../../components/CompleteInvoiceButton";
import AddToInvoiceModal from "../../components/AddToInvoiceModal/AddToInvoiceModal";
import csrfFetch from "../../utils/csrf";
import { useLocation } from "react-router-dom";

type InvoiceLine = {
  Id: string;
  Description: string;
  Amount: number;
  DetailType: string;
  customerId: string;
  SalesItemLineDetail?: {
    ItemRef: {
      name: string;
    };
    Qty: number;
    UnitPrice: number;
  };
};

export default function InvoicePage() {
  const [lines, setLines] = useState<InvoiceLine[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const location = useLocation();
  const [invoiceId, setInvoiceId] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const vehicleFromNav = location.state?.vehicle;
  const customerFromNav = location.state?.selectedCustomer;

  useEffect(() => {

    if (customerFromNav) {
      setSelectedCustomer({
        id: customerFromNav.id,
        name: customerFromNav.name || "Unknown Customer",
      });
    } else {
      const fetchCustomer = async () => {
        const resCustomer = await csrfFetch("/api/qb/session-customer", {
          credentials: "include",
        });
        const data = await resCustomer.json();
        setSelectedCustomer({
          id: data.Id,
          name: data.DisplayName,
        });
      };

      fetchCustomer();
    }
  }, []);

  if (loading) return <div className="p-4">Loading invoice…</div>;


  if (showAddModal && invoiceId && vehicleFromNav) {
    return (
      <AddToInvoiceModal
        invoiceId={invoiceId}
        customerId={customerFromNav}
        onClose={() => {
          setShowAddModal(false);
          window.location.reload();
        }}
        vehicle={vehicleFromNav}
      />
    );
  }

  return (
    <div>
      <h1>Current Invoice</h1>
      {selectedCustomer && (
        <p className="mb-2 font-semibold">
          Selected Customer: {selectedCustomer.name} (ID: {selectedCustomer.id})
        </p>
      )}
      {lines.map((line) => (
        <div key={line.Id}>
          <p>{line.SalesItemLineDetail?.ItemRef?.name || "Unnamed Item"}</p>
          <p>{line.Description}</p>
          <p>
            Qty: {line.SalesItemLineDetail?.Qty} × $
            {line.SalesItemLineDetail?.UnitPrice?.toFixed(2)}
          </p>
          <p>Total: ${line.Amount?.toFixed(2)}</p>
        </div>
      ))}

      <CompleteInvoiceButton />
    </div>
  );
}
