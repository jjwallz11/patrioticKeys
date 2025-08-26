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
          <p><strong>VIN:</strong> {vinData.VIN}</p>
          <p><strong>Make:</strong> {vinData.Make || 'N/A'}</p>
          <p><strong>Model:</strong> {vinData.Model || 'N/A'}</p>
          <p><strong>Year:</strong> {vinData.ModelYear || 'N/A'}</p>
          <p><strong>Body Class:</strong> {vinData.BodyClass || 'N/A'}</p>
          <p><strong>Vehicle Type:</strong> {vinData.VehicleType || 'N/A'}</p>
          <p><strong>Engine Cylinders:</strong> {vinData.EngineCylinders || 'N/A'}</p>
          <p><strong>Fuel Type:</strong> {vinData.FuelTypePrimary || 'N/A'}</p>
          <p><strong>Plant Country:</strong> {vinData.PlantCountry || 'N/A'}</p>
        </div>
        <div className="modal-actions">
          <button onClick={onClose} className="btn btn-primary">Close</button>
        </div>
      </div>
    </div>
  );
};

export default VinResultsModal;