// front11/src/components/ScanVinModal/ScanVinModal.tsx

import { useRef, useState, useEffect } from "react";
import Tesseract from "tesseract.js";
import { VehicleResponse } from "../../types";

type ScanVinModalProps = {
  onClose: () => void;
  setVinResult: (data: VehicleResponse) => void;
  setLastSix: (lastSix: string) => void;
  openResultsModal: () => void;
};

const ScanVinModal = ({
  onClose,
  setVinResult,
  setLastSix,
  openResultsModal,
}: ScanVinModalProps) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [vin, setVin] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      } catch (err) {
        console.error("Camera access failed", err);
      }
    };

    startCamera();
    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  const captureAndScan = async () => {
    if (!canvasRef.current || !videoRef.current) return;
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    canvasRef.current.width = videoRef.current.videoWidth;
    canvasRef.current.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0);

    setProcessing(true);
    try {
      const { data } = await Tesseract.recognize(canvasRef.current, "eng", {
        logger: (m) => console.log(m),
      });

      const match = data.text.match(/\b[A-HJ-NPR-Z0-9]{17}\b/);
      const extractedVin = match?.[0] || "";
      setVin(extractedVin || "No VIN found");

      if (extractedVin) {
        const res = await fetch(`/api/vehicle/${extractedVin}`);
        const result: VehicleResponse = await res.json();
        const lastSix = extractedVin.slice(-6);
        setLastSix(lastSix);

        const enrichedResult = { ...result, lastSix };
        setVinResult(enrichedResult);
        
        openResultsModal();
      }
    } catch (err) {
      console.error("OCR or fetch failed", err);
      setVin("Error during processing");
    }
    setProcessing(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Scan VIN</h2>
        <video ref={videoRef} className="video-preview" />
        <canvas ref={canvasRef} style={{ display: "none" }} />
        <button onClick={captureAndScan} disabled={processing}>
          {processing ? "Scanning..." : "Scan Frame"}
        </button>
        {vin && <p>Detected VIN: {vin}</p>}
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default ScanVinModal;
