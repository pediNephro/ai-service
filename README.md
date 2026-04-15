# 🧠 AI Service - PediNephro

This microservice provides AI-based analysis for medical documents in the PediNephro platform.

---

## 🚀 Features

- 📄 OCR processing (extract text from medical documents)
- 🧠 Document classification (BILAN, ORDONNANCE, AUTRE)
- ⚠️ Renal risk detection based on medical values (créatinine, urée, potassium)
- 📊 Basic AI scoring system

---

## 🏗️ Architecture

This service is part of a microservices architecture:

- medical-media-service → manages documents
- ai-service → handles AI logic
- hospitalisation-service → patient care
- frontend → Angular interface

---

## ⚙️ Technologies

- Python
- FastAPI
- Machine Learning (basic NLP logic)
- REST API

---

## 📡 API Endpoints

### 🔹 Classify document
POST /classify

### 🔹 Analyze renal risk
POST /risk

### 🔹 OCR extraction
POST /ocr

---

## ▶️ Run the project

```bash
pip install -r requirements.txt
uvicorn main:app --reload
