import { useNavigate } from "react-router-dom";
import "./Landing.css";

function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      <div className="landing-content">
        <h1>MedGuard AI</h1>
        <p className="tagline">
          Upload your hospital bill. AI checks it against official
          government rate caps and flags potential overcharges.
        </p>

        <div className="steps">
          <div className="step">
            <span className="step-number">1</span>
            <p>Upload a photo of your bill</p>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <p>AI reads and checks it against CGHS rates</p>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <p>Get a report and a ready-to-send complaint</p>
          </div>
        </div>

        <button className="btn-primary" onClick={() => navigate("/upload")}>
          Check My Bill
        </button>

        <p className="disclaimer">
          Results are estimates based on public CGHS reference rates,
          not a legal or medical determination.
        </p>
      </div>
    </div>
  );
}

export default Landing;