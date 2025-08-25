// front11/src/components/ScanVinModal/ScanVinModal.tsx

import { useRef, useState, useEffect } from "react";
import Tesseract from "tesseract.js";

type ScanVinModalProps = {
  onClose: () => void;
};

const ScanVinModal = ({ onClose }: ScanVinModalProps) => {
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
      setVin(match?.[0] || "No VIN found");
    } catch (err) {
      console.error("OCR failed", err);
      setVin("Error during OCR");
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
