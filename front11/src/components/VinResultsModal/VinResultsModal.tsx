// front11/src/components/VinResultsModal/VinResultsModal.tsx

import React from 'react';
import { VehicleResponse } from '../../types';

interface VinResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  vinData: VehicleResponse | null;
}

const VinResultsModal: React.FC<VinResultsModalProps> = ({ isOpen, onClose, vinData }) => {
  if (!isOpen || !vinData) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <h2 className="modal-title">Vehicle Details</h2>
        <div className="modal-content">
          <p><strong>VIN:</strong> {vinData.vin}</p>
          <p><strong>Make:</strong> {vinData.make || 'N/A'}</p>
          <p><strong>Model:</strong> {vinData.model || 'N/A'}</p>
          <p><strong>Year:</strong> {vinData.year || 'N/A'}</p>
          <p><strong>Body Type:</strong> {vinData.bodyType || 'N/A'}</p>
          <p><strong>Fuel Type:</strong> {vinData.fuelType || 'N/A'}</p>
          <p><strong>Manufacturer:</strong> {vinData.manufacturer || 'N/A'}</p>
          <p><strong>Plant Country:</strong> {vinData.plantCountry || 'N/A'}</p>
        </div>
        <div className="modal-actions">
          <button onClick={onClose} className="btn btn-primary">Close</button>
        </div>
      </div>
    </div>
  );
};

export default VinResultsModal;