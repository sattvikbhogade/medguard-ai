import "./ComplaintBox.css";

function ComplaintBox({ text }) {
  function handleDownload() {
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "complaint_letter.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="card complaint-box">
      <h3>Complaint Letter</h3>
      <pre className="complaint-text">{text}</pre>
      <button className="btn-primary" onClick={handleDownload}>
        Download as Text File
      </button>
    </div>
  );
}

export default ComplaintBox;