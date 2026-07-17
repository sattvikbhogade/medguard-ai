import "./LoadingSpinner.css";

function LoadingSpinner({ message }) {
  return (
    <div className="spinner-wrap">
      <div className="spinner"></div>
      <p>{message || "Loading..."}</p>
    </div>
  );
}

export default LoadingSpinner;