# 🧠 AI Service - PediNephro

## 📌 Description

This microservice provides intelligent analysis of medical documents in the PediNephro system.

It performs classification and detects renal risk based on extracted medical values.

---

## 🚀 Features

- 📄 OCR text processing
- 🧠 Document classification (BILAN, ORDONNANCE, AUTRE)
- ⚠️ Renal risk detection (créatinine, urée, potassium)
- 📊 Confidence scoring

---

## 🏗️ Architecture

This service is part of a microservices system:

- medical-media-service → document management
- ai-service → AI analysis
- hospitalisation-service → patient management

---

## ⚙️ Technologies

- Python (FastAPI)
- REST API
- Basic NLP logic

---

## 📡 API Endpoints

### 🔹 Classify document
POST /classify

### 🔹 Analyze renal risk
POST /risk

### 🔹 OCR extraction
POST /ocr

---

## 🧪 Example

### Input:
