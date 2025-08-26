// front11/src/components/ChangePasswordModal/ChangePasswordModal.tsx

import { useState } from "react";
import BaseModal from "../BaseModal/BaseModal";
import csrfFetch from "../../utils/csrf";

interface ChangePasswordModalProps {
  onClose: () => void;
}

const ChangePasswordModal = ({ onClose }: ChangePasswordModalProps) => {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setSubmitting(true);

    try {
      const res = await csrfFetch("/api/session/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
        },
        credentials: "include",
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to change password");
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Error changing password");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <BaseModal title="Change Password" onClose={onClose}>
      <div className="changepasswordmodal">
        {success ? (
          <p className="success-text">Password changed successfully!</p>
        ) : (
          <>
            <label>
              Current Password:
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </label>

            <label>
              New Password:
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </label>

            {error && <p className="error-text">{error}</p>}

            <div className="base-modal__actions">
              <button
                className="btn-edit"
                onClick={handleSubmit}
                disabled={submitting}
              >
                {submitting ? "Changing..." : "Change Password"}
              </button>
              <button className="btn-delete" onClick={onClose}>
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </BaseModal>
  );
};

export default ChangePasswordModal;