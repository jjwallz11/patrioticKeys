// src/pages/InvoicePage/InvoicePage.tsx

import { useEffect, useState } from "react";
import CompleteInvoiceButton from "../../components/CompleteInvoiceButton";
import CreateInvoiceModal from "../../components/CreateInvoiceModal";
import csrfFetch from "../../utils/csrf";
import { useLocation } from "react-router-dom";

type InvoiceLine = {
  Id: string;
  Description: string;
  Amount: number;
  DetailType: string;
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
  const customerFromNav = location.state?.selectedCustomer;

  useEffect(() => {
    const fetchInvoiceAndCustomer = async () => {
      try {
        // Fetch invoice
        const res = await csrfFetch("/api/qb/invoice", {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to load invoice");
        const data = await res.json();
        setLines(data.Line || []);

        // Fetch customer info
        const resCustomer = await csrfFetch("/api/qb/session-customer", {
          credentials: "include",
        });
        if (resCustomer.ok) {
          const customerData = await resCustomer.json();
          setSelectedCustomer({
            id: customerData.customer_id,
            name: customerData.customer_name || "Unknown Customer",
          });
        }
      } catch (err) {
        setShowCreateModal(true);
      } finally {
        setLoading(false);
      }
    };

    fetchInvoiceAndCustomer();
  }, []);

  if (loading) return <div className="p-4">Loading invoice…</div>;

  if (showCreateModal && selectedCustomer) {
    return (
      <CreateInvoiceModal
        customerId={selectedCustomer?.id}
        onClose={() => {
          setShowCreateModal(false);
          window.location.reload(); // reload to show newly created invoice
        }}
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
