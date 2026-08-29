# VisionInspect-AI

**AI-Powered Manufacturing Defect Detection and Quality Inspection System**

VisionInspect-AI is a computer-vision-based quality inspection system designed to automatically analyze manufacturing product images, detect anomalies, classify defects, estimate defect severity, and provide a final **PASS/FAIL** quality decision.

## 🚀 Features

* 📷 Product image upload
* 🔍 AI-based anomaly detection
* 🏷️ Defect classification
* 📍 Defect localization with bounding box
* 📊 Severity assessment
* ✅ PASS/FAIL quality decision
* 📋 Inspection history
* 📈 Inspection analytics
* 🌐 FastAPI backend
* ⚛️ React frontend
* 🧪 MVTec Anomaly Detection dataset support

## 🧠 AI Performance

### Anomaly Detection

| Metric    |      Score |
| --------- | ---------: |
| Accuracy  | **81.93%** |
| Precision | **98.00%** |
| Recall    | **77.78%** |
| F1 Score  | **86.73%** |

### Defect Classification

| Metric          |      Score |
| --------------- | ---------: |
| Accuracy        | **84.34%** |
| Macro Precision | **87.50%** |
| Macro Recall    | **84.39%** |
| Macro F1        | **84.58%** |

## 🏭 Supported Bottle Defects

The current implementation uses the MVTec bottle dataset and supports:

* `good`
* `broken_large`
* `broken_small`
* `contamination`

## 🏗️ System Architecture

```text
                   VisionInspect-AI
                         │
                  React Frontend
                         │
                   Image Upload
                         │
                         ▼
                  FastAPI Backend
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      Image Processing       AI Inspection
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                Anomaly       Classification   Localization
                Detection           │              │
                     └──────────────┼──────────────┘
                                    ▼
                              Severity Analysis
                                    │
                                    ▼
                              Quality Decision
                                    │
                              ┌─────┴─────┐
                              ▼           ▼
                            PASS        FAIL
                                   
                                   
                         Analytics & History
```

## 📁 Project Structure

```text
VisionInspect-AI/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── inspection.py
│   │   │   ├── analytics.py
│   │   │   └── auth.py
│   │   │
│   │   ├── services/
│   │   │   ├── anomaly_detection.py
│   │   │   ├── classification.py
│   │   │   ├── defect_classifier.py
│   │   │   ├── defect_detection.py
│   │   │   ├── image_processing.py
│   │   │   ├── inspection_history.py
│   │   │   └── severity.py
│   │   │
│   │   └── main.py
│   │
│   ├── evaluate_model.py
│   ├── evaluate_classifier.py
│   ├── evaluate_classifier_metrics.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── dataset/
│   └── mvtec/
│
├── docker-compose.yml
└── README.md
```

## ⚙️ Requirements

* Python 3.12+
* Node.js
* npm
* Git
* OpenCV
* NumPy
* Pillow
* FastAPI
* Uvicorn
* React
* Vite

## 🔧 Backend Setup

From the project root:

```bash
python -m venv venv
```

Activate the environment:

### Linux / Codespaces

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the backend:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 5000 --reload
```

Backend API:

```text
http://localhost:5000
```

Swagger documentation:

```text
http://localhost:5000/docs
```

## 💻 Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The frontend normally runs on:

```text
http://localhost:5173
```

## 📡 API Endpoints

### Inspection

```text
POST /api/inspection/inspect
```

Upload a product image and receive:

* Anomaly score
* Defect type
* Confidence
* Severity
* Quality decision
* Defect localization

### Inspection History

```text
GET /api/analytics/history
```

Returns previously completed inspections.

### Statistics

```text
GET /api/analytics/statistics
```

Returns:

* Total inspections
* Passed inspections
* Failed inspections
* Critical inspections
* Most common defect
* Defect counts

## 🧪 Dataset

The project uses the **MVTec Anomaly Detection** dataset.

Current development focuses on:

```text
dataset/mvtec/bottle/
├── train/
│   └── good/
│
└── test/
    ├── good/
    ├── broken_large/
    ├── broken_small/
    └── contamination/
```

## 🔬 Example Inspection

For a `broken_large` bottle image, the system can produce:

```text
Defect Type:       broken_large
Confidence:        100%
Anomaly Score:     10.6524
Severity:          Critical
Severity Score:    83.48 / 100
Decision:          FAIL
```

Recommended action:

```text
Reject Product and Trigger Quality Inspection Workflow
```

## 🛠️ Current Development Status

```text
MVTec Dataset                  ✅
Image Processing               ✅
Anomaly Detection              ✅
Anomaly Evaluation             ✅
Defect Classification          ✅
Classification Evaluation      ✅
Severity Assessment            ✅
PASS/FAIL Decision             ✅
Defect Localization            ✅
Bounding Box Visualization     ✅
FastAPI Backend                ✅
React Frontend                 ✅
Image Upload                   ✅
Inspection History             ✅
Analytics API                  ✅
Dashboard Statistics           ✅
```

## 🔮 Future Improvements

* Persistent database using SQLite/PostgreSQL
* User authentication
* More MVTec product categories
* Improved defect segmentation
* Advanced heatmap visualization
* Production deployment
* Real-time inspection monitoring
* Advanced analytics and charts
* Export inspection reports
* Docker-based deployment

## 👩‍💻 Project

**VisionInspect-AI**
AI-powered manufacturing defect detection and quality inspection system.
