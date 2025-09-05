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
  const [selectedCustomer, setSelectedCustomer] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const location = useLocation();
  const [invoiceId, setInvoiceId] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [invoiceMeta, setInvoiceMeta] = useState<{
    docNumber: string;
    txnDate: string;
    totalAmt: number;
  } | null>(null);
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

  useEffect(() => {
    if (!selectedCustomer) return;

    const fetchInvoice = async () => {
      try {
        const res = await csrfFetch("/api/qb/invoice/current", {
          credentials: "include",
        });
        const data = await res.json();

        setLines(data.Line || []);
        setInvoiceId(data.Id);

        setInvoiceMeta({
          docNumber: data.DocNumber,
          txnDate: data.TxnDate,
          totalAmt: data.TotalAmt,
        });
      } catch (err) {
        console.error("Failed to load invoice", err);
      } finally {
        setLoading(false);
      }
    };

    fetchInvoice();
  }, [selectedCustomer]);

  if (loading) return <div className="p-4">Loading invoice…</div>;

  if (
    (showAddModal || vehicleFromNav) &&
    invoiceId &&
    selectedCustomer &&
    vehicleFromNav
  ) {
    return (
      <AddToInvoiceModal
        invoiceId={invoiceId}
        customerId={selectedCustomer?.id}
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
      <h1 className="text-2xl font-bold mb-2">Current Invoice</h1>
      {invoiceMeta && (
        <div className="mb-4 text-sm text-gray-700">
          <p>
            Invoice #: <strong>{invoiceMeta.docNumber}</strong>
          </p>
          <p>Date: {new Date(invoiceMeta.txnDate).toLocaleDateString()}</p>
        </div>
      )}
      {selectedCustomer && (
        <p className="mb-2 font-semibold">
          Selected Customer: {selectedCustomer.name} (ID: {selectedCustomer.id})
        </p>
      )}
      {lines.map((line) => (
        <div
          key={line.Id}
          className="mb-4 p-3 border rounded bg-white shadow-sm"
        >
          <p className="font-semibold text-lg">
            {line.SalesItemLineDetail?.ItemRef?.name || "Unnamed Item"}
          </p>
          <p className="text-sm text-gray-600 italic mb-1">
            {line.Description}
          </p>
          <p>
            Qty: {line.SalesItemLineDetail?.Qty} × $
            {line.SalesItemLineDetail?.UnitPrice?.toFixed(2)}
          </p>
          <p className="font-bold">Total: ${line.Amount?.toFixed(2)}</p>
        </div>
      ))}

      {invoiceMeta && (
        <div className="mt-6 text-right font-bold text-xl">
          Invoice Total: ${invoiceMeta.totalAmt.toFixed(2)}
        </div>
      )}
      
      <CompleteInvoiceButton />
    </div>
  );
}
