import "./FindingCard.css";

const TYPE_LABELS = {
  overcharge: "Overcharge",
  duplicate_charge: "Duplicate Charge",
  vague_charge: "Vague Charge",
  generic_available: "Generic Available",
};

function FindingCard({ finding }) {
  return (
    <div className="card finding-card">
      <div className="finding-header">
        <span className={`finding-tag tag-${finding.type}`}>
          {TYPE_LABELS[finding.type] || finding.type}
        </span>
        <span className="finding-amount">Rs.{finding.charged_amount}</span>
      </div>
      <p className="finding-item">{finding.item}</p>
      <p className="finding-message">{finding.message}</p>
    </div>
  );
}

export default FindingCard;