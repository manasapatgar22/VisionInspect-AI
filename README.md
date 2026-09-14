````markdown
# VisionInspect-AI

## AI-Powered Manufacturing Defect Detection and Quality Inspection System

VisionInspect-AI is a full-stack AI-powered manufacturing quality inspection system that analyzes product images, checks image quality before inspection, detects anomalies, classifies defect types, localizes defects, scores severity, and produces a final PASS/FAIL/REVIEW quality decision.

The system includes JWT authentication, role-based access, persistent inspection records, analytics, risk assessment, and production-oriented reporting.

---

## 🚀 Features

- 🔐 JWT authentication with role-based access (`quality_engineer` / `factory_supervisor`)
- 📷 Product image upload
- 🖼️ Pre-inspection image quality analysis:
  - Sharpness
  - Brightness
  - Contrast
  - Resolution
  - Overall quality score
  - Quality rating
  - Detected image-quality issues
- 🔍 AI-based anomaly detection using a ResNet18 feature-distance model
- 🏷️ Multi-class defect classification using a prototype-based approach
- 📍 Defect localization with bounding-box overlay
- 📊 Weighted severity scoring:

  `Severity = (Size × 30%) + (Location × 25%) + (Defect Type × 25%) + (Confidence × 20%)`

- 🚦 Automated PASS / FAIL / REVIEW quality decision
- 💾 Inspection results persisted to the database
- 📋 Database-backed inspection history
- 📈 Analytics dashboard:
  - Inspection trends
  - Defect-type distribution
  - Severity distribution
  - Inspection statistics
- ⚠️ Risk assessment for detected defects
- 📤 CSV and PDF export of inspection data
- 🧭 Role-specific dashboards for Quality Engineers and Factory Supervisors
- 📝 Detailed inspection result page
- 🖼️ Image Quality Analysis report displayed in inspection results
- ⚛️ React + Vite frontend
- 📊 Recharts-based visualizations
- 🌐 FastAPI backend
- 🧪 MVTec AD dataset integration using the bottle category

---

## 📁 Project Structure

```text
VisionInspect-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application entrypoint
│   │   ├── database.py                # SQLAlchemy database/session setup
│   │   │
│   │   ├── models/
│   │   │   ├── user.py                # User/authentication model
│   │   │   └── inspection.py          # Persisted inspection records
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.py                # Registration and login
│   │   │   ├── inspection.py          # Full AI inspection pipeline
│   │   │   └── analytics.py           # History, analytics and exports
│   │   │
│   │   └── services/
│   │       ├── image_quality.py       # Sharpness, brightness, contrast, resolution
│   │       ├── anomaly_detection.py   # ResNet18 feature-distance detector
│   │       ├── defect_classifier.py   # Prototype-based defect classifier
│   │       ├── defect_detection.py    # Defect localization
│   │       ├── image_processing.py    # Image preprocessing
│   │       ├── severity.py            # Weighted severity scoring
│   │       ├── quality_control.py     # PASS/FAIL/REVIEW decision
│   │       └── inspection_report.py   # Structured inspection report
│   │
│   ├── dataset/
│   │   └── mvtec/
│   │       └── bottle/
│   │           ├── train/
│   │           │   └── good/           # Normal reference images
│   │           └── test/
│   │               ├── good/
│   │               ├── broken_large/
│   │               ├── broken_small/
│   │               └── contamination/
│   │
│   ├── evaluate_model.py               # Anomaly detector evaluation
│   ├── evaluate_classifier.py          # Classifier evaluation
│   ├── evaluate_classifier_holdout.py  # Honest held-out classification metrics/confusion matrix
│   ├── tune_threshold.py               # Anomaly threshold tuning
│   ├── test_anomaly.py                 # Anomaly detector test
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Application shell and routing
│   │   ├── main.jsx                    # React entrypoint
│   │   ├── style.css                   # Industrial dashboard styling
│   │   │
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Topbar.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── DefectChart.jsx
│   │   │   ├── TrendChart.jsx
│   │   │   ├── SeverityChart.jsx
│   │   │   ├── InspectionTable.jsx
│   │   │   ├── RiskAssessment.jsx
│   │   │   └── ImageQualityCard.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── EngineerDashboard.jsx
│   │   │   ├── SupervisorDashboard.jsx
│   │   │   ├── NewInspection.jsx
│   │   │   ├── InspectionHistory.jsx
│   │   │   ├── InspectionResult.jsx
│   │   │   ├── Analytics.jsx
│   │   │   ├── Reports.jsx
│   │   │   ├── Profile.jsx
│   │   │   └── Settings.jsx
│   │   │
│   │   └── services/
│   │       └── api.js                  # Frontend API wrapper
│   │
│   ├── vite.config.js                  # /api proxy to FastAPI
│   └── package.json
│
└── .gitignore
````

---

## ⚙️ Requirements

### Backend

* Python 3.11+
* FastAPI
* Uvicorn
* SQLAlchemy
* python-jose
* passlib
* bcrypt
* PyTorch
* torchvision
* OpenCV
* NumPy
* Pillow
* reportlab

### Frontend

* Node.js
* npm
* React
* Vite
* Recharts
* Lucide React

---

# 🔧 Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚠️ Known bcrypt Issue

If registration produces an error related to `bcrypt` or `passlib`, install:

```bash
pip install "bcrypt==4.0.1"
```

This project uses this version for compatibility with the installed Passlib configuration.

---

# 🧪 MVTec AD Dataset Setup

The anomaly detection model requires normal reference images to build its baseline.

The expected structure is:

```text
backend/
└── dataset/
    └── mvtec/
        └── bottle/
            ├── train/
            │   └── good/
            │       ├── image1.png
            │       ├── image2.png
            │       └── ...
            │
            └── test/
                ├── good/
                ├── broken_large/
                ├── broken_small/
                └── contamination/
```

Download the **bottle** category from the MVTec AD dataset and place it at:

```text
backend/dataset/mvtec/bottle/
```

If the dataset is missing or the path is incorrect, the backend may report:

```text
Model initialization failed: No images found in dataset\mvtec\bottle\train\good
```

In that case, inspection requests will not be available until the reference dataset is correctly placed.

---

# ▶️ Start the Backend

From the `backend/` directory:

```bash
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 💻 Frontend Setup

Open a new terminal:

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

Frontend:

```text
http://localhost:5173
```

The Vite configuration proxies:

```text
/api/*
```

to:

```text
http://localhost:8000
```

Make sure the backend is running before using the inspection features.

---

# 🔐 Authentication

VisionInspect-AI supports JWT-based authentication and role-based access.

Supported roles:

```text
quality_engineer
factory_supervisor
```

### Registration

A user can register through:

```text
POST /api/auth/register
```

Example:

```json
{
  "username": "demo",
  "email": "demo@test.com",
  "password": "demo1234",
  "role": "quality_engineer"
}
```

The frontend provides the login and registration interface.

After login, the JWT token is stored in:

```text
localStorage
```

using:

```text
vi_token
```

The token is sent with protected requests using:

```text
Authorization: Bearer <token>
```

If the token becomes invalid or expires, the frontend logs the user out and requests authentication again.

---

# 👥 User Roles

## Quality Engineer

The Quality Engineer can:

* Upload product images
* Run AI inspections
* View inspection results
* View defect classification
* View defect localization
* View severity analysis
* View image quality analysis
* View inspection history
* View analytics
* Generate/download reports

## Factory Supervisor

The Factory Supervisor can:

* View production quality statistics
* View inspection history
* Analyze defect trends
* Analyze severity distributions
* Review quality performance
* Access reporting and analytics

---

# 📡 API Endpoints

| Method | Path                                   | Auth | Description                                     |
| ------ | -------------------------------------- | ---- | ----------------------------------------------- |
| POST   | `/api/auth/register`                   | No   | Create a user account                           |
| POST   | `/api/auth/login`                      | No   | Get JWT access token                            |
| GET    | `/api/inspection/categories`           | No   | List available inspection categories            |
| POST   | `/api/inspection/inspect`              | Yes  | Upload image and run the AI inspection pipeline |
| GET    | `/api/analytics/history`               | No   | Retrieve inspection history                     |
| GET    | `/api/analytics/statistics`            | No   | Retrieve inspection statistics                  |
| GET    | `/api/analytics/trend`                 | No   | Retrieve daily PASS/FAIL/REVIEW trends          |
| GET    | `/api/analytics/defect-distribution`   | No   | Retrieve defect-type distribution               |
| GET    | `/api/analytics/severity-distribution` | No   | Retrieve severity distribution                  |
| GET    | `/api/analytics/export/csv`            | Yes  | Export inspection data as CSV                   |
| GET    | `/api/analytics/export/pdf`            | Yes  | Export inspection data as PDF                   |

---

# 🧠 How the Inspection Works

VisionInspect-AI follows a multi-stage inspection pipeline.

```text
Product Image
      ↓
Image Quality Analysis
      ↓
Image Preprocessing
      ↓
Anomaly Detection
      ↓
Defect Classification
      ↓
Defect Localization
      ↓
Severity Scoring
      ↓
Quality Decision
      ↓
Inspection Report
      ↓
Database + Analytics
```

---

## 1. 🖼️ Image Quality Analysis

The uploaded image is first checked before AI defect analysis.

The system analyzes:

* Resolution
* Sharpness
* Brightness
* Contrast

The image-quality module generates:

* Quality score
* Quality rating
* Detected quality issues

The frontend displays these results through the **Image Quality Analysis** card.

Example information displayed:

```text
Image Quality Analysis

Quality Score: 92 / 100
Rating: Good

Resolution: 640 × 480
Sharpness: 245.32
Brightness: 127.54
Contrast: 58.21

No image quality issues detected
```

This stage helps determine whether the uploaded image is suitable for reliable inspection.

---

## 2. 🔍 Anomaly Detection

A pretrained ResNet18 model extracts visual features from the uploaded image.

The extracted feature representation is compared with normal reference images from:

```text
MVTec AD → bottle → train → good
```

The feature distance is used as the anomaly score.

A higher anomaly score indicates greater deviation from the normal product appearance.

---

## 3. 🏷️ Defect Classification

The system uses ResNet18 feature representations and class prototypes to classify the detected defect.

For the MVTec bottle category, the current classes include:

```text
good
broken_large
broken_small
contamination
```

The classifier returns:

* Predicted defect type
* Confidence
* Anomaly status

---

## 4. 📍 Defect Localization

The system compares the inspected image against a reference image to identify the likely defect region.

The localization stage produces:

* Defect detected/not detected
* Bounding box
* Defect area percentage

The frontend displays the detected region as a bounding-box overlay on the uploaded image.

---

## 5. 📊 Severity Scoring

The system calculates a weighted severity score using:

```text
Severity Score =
(Size × 30%)
+
(Location × 25%)
+
(Defect Type × 25%)
+
(Confidence × 20%)
```

Severity levels:

|  Score | Level    |
| -----: | -------- |
| 80–100 | Critical |
|  60–79 | High     |
|  40–59 | Medium   |
|   0–39 | Low      |

The frontend presents the severity level, score, and recommended action.

---

## 6. 🚦 Quality Decision

The quality-control module combines anomaly and severity information to produce the final inspection decision.

Possible decisions:

```text
PASS
FAIL
REVIEW
```

The decision is displayed in the inspection result page and stored in the database.

---

# 📋 Inspection Result

After an inspection, the system provides a detailed result containing:

### Inspection Information

* Filename
* Timestamp
* Product category

### AI Analysis

* Anomaly score
* Defect type
* Classification confidence
* Defect localization

### Severity

* Severity score
* Severity level
* Recommended action

### Quality Control

* PASS / FAIL / REVIEW
* Decision reason

### Image Quality

* Resolution
* Sharpness
* Brightness
* Contrast
* Quality score
* Quality rating
* Quality issues

### Risk Assessment

The frontend also provides a risk assessment based on the defect, confidence, severity, and final quality decision.

---

# 📈 Analytics Dashboard

The analytics module provides database-backed quality monitoring.

Available analytics include:

### Inspection Statistics

* Total inspections
* Passed inspections
* Failed inspections
* Critical inspections

### Trend Analysis

Daily:

```text
PASS
FAIL
REVIEW
```

inspection trends are displayed using charts.

### Defect Distribution

The system shows the number of inspections associated with each predicted defect type.

### Severity Distribution

The system displays the distribution of:

```text
Low
Medium
High
Critical
```

severity levels.

---

# 📊 Reporting

VisionInspect-AI supports inspection data export in:

```text
CSV
PDF
```

The exported data can be used for:

* Quality documentation
* Production monitoring
* Inspection records
* Management reporting
* Further analysis

---

# 💾 Database

Inspection records are persisted using SQLAlchemy.

Each inspection can contain:

```text
id
filename
category
defect_type
confidence
anomaly_score
severity_score
severity_level
decision
image_quality_score
image_quality_rating
image_quality_issues
inspected_by
created_at
```

This allows inspection history and analytics to remain available after individual inspection sessions.

---

# 🧪 Model Evaluation

## Anomaly Detection — MVTec Bottle

Current evaluation results:

| Metric    | Value |
| --------- | ----: |
| Accuracy  |  0.93 |
| Precision |  0.98 |
| Recall    |  0.92 |
| F1 Score  |  0.95 |

The anomaly threshold is tuned using the distance distribution of normal images.

The current threshold configuration was selected using the available labeled bottle test set.

Run:

```bash
python tune_threshold.py
```

if the reference dataset or evaluation setup changes.

---

# 🏷️ Defect Classification Evaluation

Evaluated with a genuine held-out split: for each class, 10 images are used only to build prototypes, and the remaining images (never seen while building prototypes) are used only for evaluation. See `evaluate_classifier_holdout.py`.

| Class             | Precision |   Recall | F1 Score | n (held-out) |
| ----------------- | --------: | -------: | -------: | ------------: |
| broken_large      |      1.00 |     0.80 |     0.89 |            10 |
| broken_small      |      0.77 |     0.83 |     0.80 |            12 |
| contamination     |      1.00 |     0.64 |     0.78 |            11 |
| good              |      0.67 |     1.00 |     0.80 |            10 |
| **Macro Average** |  **0.86** | **0.82** | **0.82** |            43 |

Overall accuracy:

```text
0.8140 (35/43 correct)
```

---

# ⚠️ Evaluation Notes & Known Limitation

The current `DefectClassifier` is a prototype-based nearest-centroid baseline using ResNet18 features.

This is a genuine held-out evaluation: prototypes are built from a support set, and metrics are computed only on a disjoint query set of images the classifier never saw while building those prototypes. (An earlier version of this evaluation built prototypes and computed metrics from the same `test/` directory, which inflated accuracy to ~0.83; that overlap has been fixed.)

**Known limitation:** `good` has perfect recall (1.00) but the lowest precision (0.67) of any class — 5 held-out defect images (3 `contamination`, 2 `broken_small`) were misclassified as `good`. In a QC system this is the highest-priority error type, since it means real defects could be passed through as non-defective. Improving this is planned future work (see below), for example by increasing the number of support images per class or normalizing extracted features before computing distances to prototypes.

Held-out support/query sizes are still small (10–12 images per class), since the MVTec `test/` split for `bottle` only has 20–22 images per class total. Results should be read as directionally honest rather than statistically precise.

---

# 🛠️ Troubleshooting

## 1. bcrypt / Passlib Error

### Error

```text
AttributeError: module 'bcrypt' has no attribute '__about__'
```

or:

```text
password cannot be longer than 72 bytes
```

### Fix

```bash
pip install "bcrypt==4.0.1"
```

---

## 2. Dataset Not Found

### Error

```text
Model initialization failed: No images found in dataset\mvtec\bottle\train\good
```

### Fix

Ensure the dataset exists at:

```text
backend/dataset/mvtec/bottle/train/good/
```

---

## 3. Frontend ECONNREFUSED

### Error

```text
ECONNREFUSED
```

### Possible causes

* Backend is not running
* Backend is running on another port
* Vite proxy target is incorrect

### Fix

Start the backend:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Then verify that:

```text
http://127.0.0.1:8000
```

is available.

Also verify the frontend proxy configuration in:

```text
frontend/vite.config.js
```

---

# 📌 Current Project Status

## Milestone 1

### Completed

* Project planning
* System architecture
* AI inspection workflow
* Backend foundation
* Database design
* Authentication
* Initial frontend structure

---

## Milestone 2

### Completed

* Image preprocessing
* Image quality analysis
* ResNet18-based anomaly detection
* Defect classification
* Defect localization
* Severity scoring
* PASS/FAIL/REVIEW decision
* Database persistence
* MVTec bottle integration
* Initial analytics
* Working frontend dashboard

---

## Milestone 3

### Completed / Integrated

* Defect categorization workflows
* Severity assessment
* Risk assessment
* Image quality assessment
* Inspection result reporting
* Inspection history
* Production quality analytics
* Defect distribution
* Severity distribution
* Trend monitoring
* CSV/PDF reporting
* Role-specific dashboards
* Image Quality Analysis visualization
* Responsive industrial UI

---

# 🚧 Future Work / Milestone 4

The following improvements can be addressed during final validation and deployment:

* ~~Create a genuine held-out split for defect-classification evaluation~~ ✅ Done — see Defect Classification Evaluation above
* Reduce good/defect confusion (5 held-out defects misclassified as `good`) — try more support images per class and/or feature normalization
* Improve classifier performance with a trained production classifier
* Add more comprehensive image-quality aggregate analytics
* Expand PDF reports with detailed image-quality metrics
* Docker containerization
* Cloud deployment
* Production deployment validation
* Final system testing and performance evaluation

---

# 🏆 Project Highlights

VisionInspect-AI combines multiple computer-vision and software-engineering components into a single manufacturing quality-inspection workflow:

```text
Authentication
      ↓
Image Upload
      ↓
Image Quality Analysis
      ↓
AI Anomaly Detection
      ↓
Defect Classification
      ↓
Defect Localization
      ↓
Severity Assessment
      ↓
Risk Assessment
      ↓
PASS / FAIL / REVIEW
      ↓
Database Persistence
      ↓
Analytics & Reporting
```

The project demonstrates the integration of:

* Artificial Intelligence
* Computer Vision
* Deep Learning
* FastAPI
* React
* SQLAlchemy
* JWT Authentication
* Data Analytics
* Automated Quality Control
* Production-oriented Reporting

---

## 👨‍💻 Project

**VisionInspect-AI**

AI-Powered Manufacturing Defect Detection and Quality Inspection System