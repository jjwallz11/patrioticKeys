// src/pages/InvoicePage/InvoicePage.tsx

import { useEffect, useState } from "react";
import CompleteInvoiceButton from "../../components/CompleteInvoiceButton";
import csrfFetch from "../../utils/csrf";

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
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchInvoice = async () => {
      try {
        const res = await csrfFetch("/api/qb/invoice", {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to load invoice");
        const data = await res.json();
        setLines(data.Line || []);
      } catch (err) {
        setError("Error fetching invoice");
      } finally {
        setLoading(false);
      }
    };

    fetchInvoice();
  }, []);

  if (loading) return <div className="p-4">Loading invoice…</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div>
      <h1>Current Invoice</h1>
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
