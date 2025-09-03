// front11/src/components/BaseModal/BaseModal.tsx

import React from "react";
// import "./BaseModal.css";

interface BaseModalProps {
  isOpen?: boolean;
  title?: string;
  onClose: () => void;
  onSave?: () => void;
  showButtons?: boolean;
  children: React.ReactNode;
}

const BaseModal = ({ isOpen = true, title, onClose, onSave, showButtons = true, children }: BaseModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="base-modal__overlay">
      <div className="base-modal__card">
        {title && <div className="base-modal__header">{title}</div>}

        <div className="base-modal__body">{children}</div>

        {showButtons && (
          <div className="base-modal__actions">
            <button className="btn-edit" onClick={() => onSave?.()}>Save</button>
            <button className="btn-delete" onClick={onClose}>Cancel</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BaseModal;