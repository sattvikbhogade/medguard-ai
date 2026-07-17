# 🏥 MedGuard AI – AI-Powered Medical Bill Auditing Platform

MedGuard AI is an AI-powered healthcare application that helps patients understand and verify their medical bills. It analyzes hospital bills using Artificial Intelligence, detects possible billing irregularities, and generates easy-to-understand audit reports, promoting transparency and informed healthcare decisions.

---

## 📌 Problem Statement

Medical bills are often complex and difficult for patients to understand. Many people are unable to verify whether they have been charged correctly, leading to unnoticed overcharges, duplicate billing, expensive branded medicines, and unclear charges.

MedGuard AI addresses this challenge by automatically auditing hospital bills and highlighting potential issues before patients make payments.

---

## ✨ Features

* 📄 Upload medical bills (Image or PDF)
* 🤖 AI-powered data extraction using Google Gemini
* 🔍 Detect possible overcharges
* 🔄 Identify duplicate billing
* 💊 Suggest generic medicine alternatives
* 📊 Generate a transparency score
* 📋 Create a detailed audit report
* 📝 Generate complaint drafts for suspicious billing

---

## 🚀 How It Works

1. Upload a hospital bill (Image or PDF).
2. Gemini AI extracts bill details into structured data.
3. The analysis engine checks for:

   * Overcharges
   * Duplicate billing
   * Generic medicine alternatives
   * Missing or unclear billing information
4. The system generates:

   * Transparency Score
   * Audit Report
   * Complaint Draft (if required)

---

## 🏗️ System Workflow

```text
Patient
   │
   ▼
Upload Medical Bill
   │
   ▼
Gemini AI OCR & Extraction
   │
   ▼
Structured Medical Data
   │
   ▼
Analysis Engine
   │
   ▼
Reference Medical Database
   │
   ▼
Issue Detection
   │
   ▼
Transparency Score
   │
   ▼
Audit Report
   │
   ▼
Complaint Generator
```

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* HTML
* CSS
* JavaScript

### Backend

* FastAPI
* Python

### Database

* PostgreSQL

### ORM

* SQLAlchemy

### Database Migration

* Alembic

### AI

* Google Gemini API

### Deployment

* Vercel (Frontend)
* Render (Backend)

### Version Control

* Git & GitHub

---

## 📂 Project Structure

```text
medguard-ai/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   ├── main.py
│   └── ...
│
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/sattvikbhogade/medguard-ai.git
cd medguard-ai
```

### Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend will run at:

```text
http://localhost:8000
```

Swagger API Documentation:

```text
http://localhost:8000/docs
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

---

## 📊 Sample Output

After analyzing a medical bill, MedGuard AI provides:

* Extracted Hospital Details
* Itemized Bill Analysis
* Transparency Score
* Suspicious Billing Findings
* Generic Medicine Suggestions
* Complaint Draft

---

## 🎯 Future Scope

* Insurance claim verification
* Government grievance portal integration
* Hospital price database expansion
* Multilingual support
* Mobile application
* Advanced AI fraud detection
* Analytics dashboard

---

## 🌍 Impact

MedGuard AI aims to:

* Improve healthcare transparency
* Help patients understand medical bills
* Reduce financial burden caused by billing errors
* Promote fair healthcare billing
* Empower patients to make informed financial decisions

---

## 👨‍💻 Author

**Sattvik Bhogade**

GitHub: https://github.com/sattvikbhogade

---

## 📄 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
