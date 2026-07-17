import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { generateComplaint } from "../services/api";
import ScoreCard from "../components/ScoreCard";
import FindingCard from "../components/FindingCard";
import ComplaintBox from "../components/ComplaintBox";
import LoadingSpinner from "../components/LoadingSpinner";
import "./Report.css";

function Report() {
  const location = useLocation();
  const navigate = useNavigate();
  const { analysis, filename } = location.state || {};

  const [complaintText, setComplaintText] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  if (!analysis) {
    return (
      <div className="container">
        <p>No report data found.</p>
        <button className="btn-primary" onClick={() => navigate("/upload")}>
          Upload a Bill
        </button>
      </div>
    );
  }

  async function handleGenerateComplaint() {
    setGenerating(true);
    setError(null);
    try {
      const result = await generateComplaint(filename);
      setComplaintText(result.complaint_text);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not generate complaint. Please try again."
      );
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="container">
      <ScoreCard
        score={analysis.transparency_score}
        riskLevel={analysis.risk_level}
        hospitalName={analysis.hospital_name}
        totalFindings={analysis.total_findings}
      />

      <h3 className="findings-title">Potential Issues</h3>

      {analysis.findings.length === 0 ? (
        <div className="card">
          <p>No issues found. This bill looks consistent with reference rates.</p>
        </div>
      ) : (
        analysis.findings.map((finding, idx) => (
          <FindingCard key={idx} finding={finding} />
        ))
      )}

      {!complaintText && (
        <div className="complaint-action">
          {error && <p className="error-text">{error}</p>}
          {generating ? (
            <LoadingSpinner message="Drafting your complaint letter..." />
          ) : (
            <button
              className="btn-primary"
              onClick={handleGenerateComplaint}
              disabled={analysis.findings.length === 0}
            >
              Generate Complaint Letter
            </button>
          )}
        </div>
      )}

      {complaintText && <ComplaintBox text={complaintText} />}

      <button className="btn-secondary" onClick={() => navigate("/upload")}>
        Check Another Bill
      </button>
    </div>
  );
}

export default Report;