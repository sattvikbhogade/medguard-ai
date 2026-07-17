import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export async function uploadBill(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data; // { status, filename }
}

export async function analyzeBill(filename) {
  const response = await axios.post(`${API_BASE}/analyze`, null, {
    params: { filename },
  });
  return response.data; // { hospital_name, bill_date, transparency_score, risk_level, findings, ... }
}

export async function generateComplaint(filename) {
  const response = await axios.post(`${API_BASE}/complaint`, null, {
    params: { filename },
  });
  return response.data; // { complaint_text }
}