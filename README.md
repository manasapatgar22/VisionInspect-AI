# VisionInspect-AI

**AI-Powered Manufacturing Defect Detection and Quality Inspection System**

VisionInspect-AI analyzes manufacturing product images, detects anomalies,
classifies defect types, localizes defects, scores severity, and produces a
final PASS/FAIL/REVIEW quality decision — with JWT-authenticated,
role-restricted access and persistent inspection records.

## 🚀 Features

* 🔐 JWT authentication with role-based access (`quality_engineer` / `factory_supervisor`)
* 📷 Product image upload
* 🔍 AI-based anomaly detection (ResNet18 feature-distance model)
* 🏷️ Multi-class defect classification (prototype-based)
* 📍 Defect localization with bounding box overlay
* 📊 Weighted severity scoring — `(Size × 30%) + (Location × 25%) + (Type × 25%) + (Confidence × 20%)`
* ✅ Automated PASS / FAIL / REVIEW decision
* 💾 Inspection results persisted to the database
* 📈 Basic inspection statistics dashboard
* ⚛️ React + Vite frontend, dashboard-style UI with severity color coding
* 🌐 FastAPI backend
* 🧪 Built against the MVTec AD dataset (bottle category)

## 📁 Project Structure

```text
VisionInspect-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entrypoint
│   │   ├── database.py              # SQLAlchemy Base / session / get_db
│   │   ├── models/
│   │   │   ├── user.py              # User table (auth)
│   │   │   └── inspection.py        # InspectionRecord table (persisted results)
│   │   ├── routes/
│   │   │   ├── auth.py              # register, login, get_current_user
│   │   │   ├── inspection.py        # /inspect — the full AI pipeline
│   │   │   └── analytics.py         # /statistics (used by the dashboard)
│   │   └── services/
│   │       ├── anomaly_detection.py # MVTecAnomalyDetector (ResNet18 feature distance)
│   │       ├── defect_classifier.py # DefectClassifier (prototype-based)
│   │       ├── defect_detection.py  # localize_defect (bounding box)
│   │       ├── image_processing.py  # preprocess_image
│   │       ├── severity.py          # calculate_severity
│   │       ├── quality_control.py   # make_quality_decision
│   │       ├── inspection_report.py # create_inspection_report
│   │       └── inspection_history.py# add_inspection (in-memory recent list)
│   ├── dataset/
│   │   └── mvtec/bottle/
│   │       ├── train/good/          # reference images for the anomaly baseline
│   │       └── test/                # good / broken_large / broken_small / contamination
│   ├── evaluate_model.py            # standalone anomaly detector evaluation script
│   ├── test_anomaly.py              # standalone anomaly detector test script
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # login gate + dashboard + upload + results
│   │   ├── main.jsx                 # React entrypoint
│   │   └── style.css                # dashboard/industrial theme
│   ├── vite.config.js               # proxies /api/* to the backend
│   └── package.json
│
└── .gitignore
```

## ⚙️ Requirements

* Python 3.11+
* Node.js + npm
* FastAPI, Uvicorn
* SQLAlchemy
* python-jose, passlib, `bcrypt==4.0.1` (see note below)
* PyTorch, torchvision
* OpenCV, NumPy, Pillow
* React, Vite

## 🔧 Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```
Create the environment:python -m venv venv
Use code with caution.Activate it: .\venv\Scripts\Activate.ps1


> **Known issue:** `bcrypt` 4.1+ breaks `passlib`'s password hashing —
> registration will fail with `AttributeError: module 'bcrypt' has no
> attribute '__about__'` or `password cannot be longer than 72 bytes`.
> Fix:
> ```bash
> pip install "bcrypt==4.0.1"
> ```

Add the reference dataset before starting the server — the anomaly detector
needs it to build its "normal" baseline:

```text
backend/dataset/mvtec/bottle/train/good/*.png
backend/dataset/mvtec/bottle/test/{good,broken_large,broken_small,contamination}/*.png
```

Download the "bottle" category from the
[MVTec AD dataset](https://www.mvtec.com/company/research/datasets/mvtec-ad)
and place it at that exact path. If the path doesn't match, startup logs:
```
Model initialization failed: No images found in dataset\mvtec\bottle\train\good
```
and `/api/inspection/inspect` returns `500: Inspection models are not ready.`

Start the backend (from inside `backend/`):

```bash
python -m uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## 💻 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Frontend: `http://localhost:5173`

Vite proxies `/api/*` calls to the backend. **Check `vite.config.js`'s proxy
target matches the port the backend is actually running on** (`8000` per the
command above) — a mismatch here is the most common cause of
`ECONNREFUSED` proxy errors, along with simply not having the backend
running yet.

## 🔐 Authentication

`/api/inspection/inspect` requires a valid JWT and one of two roles.

1. Register via Swagger (`POST /api/auth/register`):
   ```json
   {
     "username": "demo",
     "email": "demo@test.com",
     "password": "demo1234",
     "role": "quality_engineer"
   }
   ```
   Valid roles: `quality_engineer`, `factory_supervisor`. Any other role is
   rejected by the inspection endpoint with `403`.
2. Log in through the frontend — it shows a login screen automatically
   whenever there's no stored token.
3. The JWT is stored in `localStorage` (`vi_token`) and sent as
   `Authorization: Bearer <token>` on every inspection request.
4. A `401` response (expired/invalid token) automatically logs the user out
   and prompts them to sign in again.

## 📡 API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create a user account |
| POST | `/api/auth/login` | No | Get a JWT access token |
| POST | `/api/inspection/inspect` | Yes (role-restricted) | Upload an image, run the full AI pipeline, persist the result |
| GET | `/api/analytics/statistics` | — | Stats shown on the dashboard (total/passed/failed/critical) |

## 🧠 How Inspection Works

1. **Anomaly detection** — a pretrained ResNet18 extracts features from the
   uploaded image and compares them against the "good" reference set; the
   distance is the anomaly score.
2. **Classification** — the same feature space is compared against
   per-class prototypes built from the test set to predict a specific
   defect type (`good`, `broken_large`, `broken_small`, `contamination`).
3. **Localization** — the uploaded image is diffed against a reference
   image to produce a bounding box around the likely defect region, drawn
   as an overlay in the frontend.
4. **Severity** — the weighted formula above maps to Critical (80-100) /
   High (60-79) / Medium (40-59) / Low (0-39), each shown with a distinct
   color in the UI.
5. **Quality decision** — anomaly score + severity together produce
   PASS / FAIL / REVIEW, which is displayed and saved to the database.

## ✅ Status

**Done and verified working:**
- Auth, role-based access control
- Dataset-backed anomaly detection, classification, localization
- Severity scoring, quality decision
- Inspection results persisted to the database (`InspectionRecord`)
- Dashboard-style frontend with severity color coding

**Known gaps / next steps:**
- `InspectionRecord` rows are written on every inspection, but no endpoint
  currently reads them back — `GET /api/analytics/statistics` and any
  `/history` view still rely on the in-memory `inspection_history` list,
  which resets on server restart. Wiring a DB-backed history endpoint is
  the next real improvement.
- `evaluate_model.py` / `test_anomaly.py` exist but haven't been run for a
  documented precision/recall/F1 report — worth doing before citing
  specific accuracy numbers anywhere.
- No formal UI wireframes were produced — the working UI was built
  directly instead.
- Docker/cloud deployment not yet attempted (planned for later per the
  original project's week-by-week schedule).

## 🐛 Troubleshooting Log

Issues actually hit and fixed while building this:

| Symptom | Cause | Fix |
|---|---|---|
| `backend/app/models/` missing after cloning | `.gitignore` had a bare `models/` line meant for PyTorch checkpoints, which also matched the SQLAlchemy models folder | Changed to `*.pth` / `*.pt` / `*.onnx` only |
| `password cannot be longer than 72 bytes` on register | `bcrypt` 4.1+ incompatible with installed `passlib` | `pip install "bcrypt==4.0.1"` |
| `Model initialization failed: No images found in dataset\mvtec\bottle\train\good` | Dataset folder empty or wrong path | Place MVTec images at `backend/dataset/mvtec/bottle/train/good/` |
| Frontend `ECONNREFUSED` on every `/api/*` call | Backend not running, or `vite.config.js` proxy target pointed at the wrong port | Start backend first; confirm proxy target matches `8000` |