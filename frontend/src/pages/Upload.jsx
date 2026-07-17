import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadBill, analyzeBill } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import "./Upload.css";

function Upload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  function handleFileChange(e) {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError(null);
  }

  async function handleAnalyze() {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      setLoadingStep("Uploading bill...");
      const uploadResult = await uploadBill(file);

      setLoadingStep("Reading document and checking rates...");
      const analysis = await analyzeBill(uploadResult.filename);

      navigate("/report", {
        state: { analysis, filename: uploadResult.filename },
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Something went wrong. Please try again."
      );
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container">
        <LoadingSpinner message={loadingStep} />
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card upload-card">
        <h2>Upload Your Bill</h2>
        <p className="upload-sub">Photo or scan of an itemized hospital bill</p>

        <label className="upload-box">
          {preview ? (
            <img src={preview} alt="Bill preview" className="preview-img" />
          ) : (
            <div className="upload-placeholder">
              <span>+ Choose Image</span>
            </div>
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            hidden
          />
        </label>

        {error && <p className="error-text">{error}</p>}

        <button
          className="btn-primary"
          onClick={handleAnalyze}
          disabled={!file}
        >
          Analyze Bill
        </button>
      </div>
    </div>
  );
}

export default Upload;