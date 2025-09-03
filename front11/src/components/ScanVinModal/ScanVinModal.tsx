// front11/src/components/ScanVinModal/ScanVinModal.tsx

import { useRef, useState, useEffect } from "react";
import Tesseract from "tesseract.js";
import { VehicleResponse } from "../../types";
import csrfFetch from "../../utils/csrf";
import BaseModal from "../BaseModal/BaseModal";
import "./ScanVinModal.css";

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
  const vinFoundRef = useRef(false);

  useEffect(() => {
    let scanning = true;

    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { exact: "environment" } },
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();

          // Start scanning loop
          const scanInterval = setInterval(async () => {
            if (
              !vinFoundRef.current &&
              scanning &&
              videoRef.current?.readyState === 4
            ) {
              const success = await captureAndScan(true);
              if (success) {
                vinFoundRef.current = true;
                clearInterval(scanInterval);
              }
            }
          }, 1000);

          // Timeout if nothing is found
          setTimeout(() => {
            if (!vinFoundRef.current) {
              setVin("No VIN found");
              clearInterval(scanInterval);
            }
            scanning = false;
          }, 7000);
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

  const captureAndScan = async (silent = false): Promise<boolean> => {
    if (!canvasRef.current || !videoRef.current) return false;
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return false;

    canvasRef.current.width = videoRef.current.videoWidth;
    canvasRef.current.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0);

    try {
      const { data } = await Tesseract.recognize(canvasRef.current, "eng", {
        logger: (m) => console.log(m),
      });

      const match = data.text.match(/\b[A-HJ-NPR-Z0-9]{17}\b/);
      const extractedVin = match?.[0] || "";
      if (extractedVin) {
        setVin(extractedVin);
        const res = await csrfFetch(`/api/vehicles/${extractedVin}`);
        const result: VehicleResponse = await res.json();
        const lastSix = extractedVin.slice(-6);
        setLastSix(lastSix);
        setVinResult({ ...result, lastSix });
        openResultsModal();
        return true;
      } else if (!silent) {
        setVin("No VIN found");
      }
    } catch (err) {
      console.error("OCR or fetch failed", err);
      if (!silent) setVin("Error during processing");
    }

    return false;
  };

  return (
    <div className="modal scan-vin-modal">
      <BaseModal title="Scan VIN" onClose={onClose} showButtons={false}>
        <div className="scan-vin-modal__video-wrapper">
          <video ref={videoRef} className="scan-vin-modal__video" />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          {processing && <p>Scanning...</p>}
          {vin && <p>Detected VIN: {vin}</p>}
        </div>
      </BaseModal>
    </div>
  );
};

export default ScanVinModal;
