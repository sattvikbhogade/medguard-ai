import "./ScoreCard.css";

function ScoreCard({ score, riskLevel, hospitalName, totalFindings }) {
  let colorClass = "score-green";
  if (score < 60) colorClass = "score-red";
  else if (score < 85) colorClass = "score-yellow";

  return (
    <div className="card score-card">
      <div className="score-header">
        <div>
          <p className="hospital-name">{hospitalName || "Hospital bill"}</p>
          <p className="findings-count">
            {totalFindings} potential {totalFindings === 1 ? "issue" : "issues"} found
          </p>
        </div>
        <div className={`score-circle ${colorClass}`}>
          <span>{score}</span>
        </div>
      </div>
      <p className={`risk-label ${colorClass}`}>{riskLevel}</p>
    </div>
  );
}

export default ScoreCard;