// front11/src/components/ItemSelectModal/ItemSelectModal.tsx

import { useEffect, useState } from "react";
import BaseModal from "../BaseModal/BaseModal";
import csrfFetch from "../../utils/csrf";

interface QBItem {
  id: string;
  name: string;
  description?: string;
}

interface ItemSelectModalProps {
  onClose: () => void;
  onItemSelect: (item: QBItem) => void;
}

const ItemSelectModal = ({ onClose, onItemSelect }: ItemSelectModalProps) => {
  const [items, setItems] = useState<QBItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const res = await csrfFetch("/api/qb/items", {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to load items");
        const data = await res.json();
        setItems(
          (data.items || []).map((item: any) => ({
            id: item.Id,
            name: item.Name,
            description: item.Description,
          }))
        );
      } catch (err: any) {
        setError(err.message || "Error loading items");
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  const handleSelect = (item: QBItem) => {
    onItemSelect(item);
    onClose();
  };

  return (
    <BaseModal title="Select an Item" onClose={onClose}>
      <div className="item-select-modal__body">
        {loading && <p>Loading items...</p>}
        {error && <p className="error-text">{error}</p>}
        {!loading && !error && items.length === 0 && <p>No items available.</p>}

        <ul className="item-list">
          {items.map((item) => (
            <li key={item.id}>
              <button className="btn-edit" onClick={() => handleSelect(item)}>
                {item.name}
              </button>
            </li>
          ))}
        </ul>

        <div className="base-modal__actions">
          <button className="btn-delete" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </BaseModal>
  );
};

export default ItemSelectModal;
