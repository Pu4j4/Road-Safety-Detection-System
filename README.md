# 🚗 Road Safety Detection System

An AI-powered road safety analysis web application built with **Django**, **Django REST Framework**, **YOLOv8**, and a **CNN lane detection model**. Detects potholes and lane boundaries from uploaded images and videos, with automated SMS alerts to municipalities via Twilio.

---

## 📸 Screenshots

### Dashboard
![Dashboard](https://github.com/Pu4j4/Road-Safety-Detection-System/blob/main/screenshots/RDLD1.JPG?raw=true)

### Pothole Detection — Upload
![Pothole Detection](https://github.com/Pu4j4/Road-Safety-Detection-System/blob/main/screenshots/RDLD2.JPG?raw=true)

### Lane Detection — Upload
![Lane Detection](https://github.com/Pu4j4/Road-Safety-Detection-System/blob/main/screenshots/RDLD3.JPG?raw=true)

### Pothole Detection — Result with Bounding Boxes
![Pothole Result](https://github.com/Pu4j4/Road-Safety-Detection-System/blob/main/screenshots/RDLD4.JPG?raw=true)

### Detection History — Detail View
![Detection Detail](https://github.com/Pu4j4/Road-Safety-Detection-System/blob/main/screenshots/RDLD5.JPG?raw=true)

---

## ✨ Features

- 🕳️ **Pothole Detection** — Upload road images or videos; YOLOv8 detects and marks potholes with red bounding boxes
- 🛣️ **Lane Detection** — Upload dashcam videos; CNN model overlays detected lane boundaries with a green mask
- 📨 **SMS Alerts** — Automatically notify municipality via Twilio SMS when potholes are detected
- 📋 **Detection History** — All detections saved to database with full metadata and result files
- ⚙️ **Django Admin** — Manage detection records and alert logs via built-in admin panel
- 🔌 **REST API** — Full DRF API for all detection and alert operations

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Django 4.2 |
| REST API | Django REST Framework |
| Pothole Detection | YOLOv8 (Ultralytics) |
| Lane Detection | CNN (full_CNN_model.h5 via tf_keras) |
| Database | SQLite |
| SMS Alerts | Twilio |
| Image Processing | OpenCV, Pillow, scikit-image |
| Deep Learning | TensorFlow 2.21, tf_keras |
| Frontend | HTML + CSS + Vanilla JS (dark theme) |

---

## 📁 Project Structure

```
RoadSafetyDetectionSystem/
│
├── manage.py
├── requirements.txt
├── .gitignore
├── .env.example
│
├── road_safety_detection_system/       # Django config package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── detection/                          # Main Django app
│   ├── models.py                       # DetectionRecord, AlertLog
│   ├── admin.py                        # Django admin config
│   ├── apps.py                         # Loads ML models at startup
│   ├── views.py                        # HTML page views
│   ├── urls.py                         # Frontend routes
│   ├── serializers.py                  # DRF serializers
│   ├── api_views.py                    # DRF API endpoints
│   ├── api_urls.py                     # API routes
│   ├── ml_service.py                   # Model loading + inference
│   ├── alert_service.py                # Twilio SMS service
│   ├── migrations/
│   └── templates/detection/
│       ├── base.html
│       ├── dashboard.html
│       ├── pothole_detection.html
│       ├── lane_detection.html
│       ├── history.html
│       └── detail.html
│
└── model/                              # Place model weights here (not tracked by git)
    ├── full_CNN_model.h5
    └── best.pt
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Pu4j4/Road-Safety-Detection-System.git
cd Road-Safety-Detection-System
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install tf_keras
```

### 4. Place model files

Create the `model/` folder and add your trained model files:

```
model/
├── full_CNN_model.h5    ← Lane detection CNN
└── best.pt              ← Pothole detection YOLOv8
```

### 5. Configure environment variables

```powershell
# Windows PowerShell
$env:TWILIO_SID="your_account_sid"
$env:TWILIO_AUTH_TOKEN="your_auth_token"
$env:TWILIO_PHONE_NUMBER="+1XXXXXXXXXX"
$env:MUNICIPALITY_PHONE="+91XXXXXXXXXX"
```

```bash
# Mac/Linux
export TWILIO_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="+1XXXXXXXXXX"
export MUNICIPALITY_PHONE="+91XXXXXXXXXX"
```

### 6. Run migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Start the server

```bash
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000/**

---

## 🌐 URL Routes

### Frontend Pages

| URL | Page |
|-----|------|
| `/` | Dashboard — stats and recent detections |
| `/pothole/` | Pothole Detection — upload image or video |
| `/lane/` | Lane Detection — upload video |
| `/history/` | Detection History — all records |
| `/history/<id>/` | Detection Detail — single record |
| `/admin/` | Django Admin Panel |

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/detect/pothole/` | Run pothole detection on image/video |
| `POST` | `/api/detect/lane/` | Run lane detection on video |
| `POST` | `/api/alert/send/` | Send Twilio SMS alert |
| `GET` | `/api/history/` | List all detection records |
| `GET` | `/api/history/<id>/` | Get single detection record |
| `GET` | `/api/stats/` | Dashboard statistics |

---

## 📡 API Usage

### Pothole Detection

```bash
curl -X POST http://localhost:8000/api/detect/pothole/ \
  -F "file=@road_image.jpg"
```

**Response:**
```json
{
  "success": true,
  "message": "Potholes detected! (17 detections)",
  "data": {
    "id": 1,
    "detection_type": "pothole",
    "media_type": "image",
    "status": "completed",
    "pothole_count": 17,
    "pothole_detected": true,
    "processing_time_ms": 1008.0,
    "result_file_url": "http://localhost:8000/media/results/pothole_result_1.jpg"
  }
}
```

### Lane Detection

```bash
curl -X POST http://localhost:8000/api/detect/lane/ \
  -F "file=@dashcam.mp4"
```

### Send Alert

```bash
curl -X POST http://localhost:8000/api/alert/send/ \
  -H "Content-Type: application/json" \
  -d '{"detection_id": 1}'
```

### Filter History

```bash
# Pothole detections only
curl "http://localhost:8000/api/history/?type=pothole"

# Completed records only
curl "http://localhost:8000/api/history/?status=completed"
```

---

## 🗄️ Database Models

### DetectionRecord

| Field | Type | Description |
|-------|------|-------------|
| `detection_type` | CharField | `pothole` or `lane` |
| `media_type` | CharField | `image` or `video` |
| `input_file` | FileField | Original uploaded file |
| `result_file` | FileField | Annotated output file |
| `status` | CharField | `pending / processing / completed / failed` |
| `pothole_count` | IntegerField | Number of potholes detected |
| `pothole_detected` | BooleanField | True if any potholes found |
| `alert_sent` | BooleanField | True if SMS was sent |
| `processing_time_ms` | FloatField | Inference time in milliseconds |

### AlertLog

| Field | Type | Description |
|-------|------|-------------|
| `detection` | ForeignKey | Related DetectionRecord |
| `phone_number` | CharField | Recipient phone number |
| `message_sid` | CharField | Twilio message SID |
| `success` | BooleanField | Whether SMS was delivered |
| `error_message` | TextField | Error details if failed |

---

## 🤖 ML Models

### Lane Detection — CNN
- **Architecture:** Full Convolutional Neural Network
- **Input size:** 160 × 80 pixels
- **Output:** Green lane mask overlaid at 1280 × 720
- **Smoothing:** 5-frame rolling average for stable detection
- **Format:** `.h5` loaded via `tf_keras` for TF 2.16+ compatibility

### Pothole Detection — YOLOv8
- **Architecture:** YOLOv8n (nano)
- **Training data:** Roboflow pothole dataset + custom annotations
- **Output:** Red bounding boxes with confidence scores
- **Format:** `.pt` PyTorch weights via Ultralytics

---

## 📦 Requirements

```
django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.0
tensorflow>=2.13
tf_keras
ultralytics>=8.0
opencv-python-headless>=4.8
scikit-image>=0.21
Pillow>=10.0
numpy>=1.24
twilio>=8.0
```

---

## 🚀 Migration from Streamlit

This project was originally built with Streamlit on Google Colab and migrated to Django + DRF.

| Streamlit (Original) | Django + DRF (This Project) |
|---------------------|----------------------------|
| `st.file_uploader()` | DRF `MultiPartParser` |
| `st.image()` / `st.video()` | HTML `<img>` / `<video>` |
| No persistence | Django ORM + SQLite |
| No admin panel | Full Django Admin |
| ngrok tunnel | Production-ready WSGI |

---

## 👨‍💻 Author

**Bhanupooja Bethala** — [@Pu4j4](https://github.com/Pu4j4)

---

## 📄 License

This project is for educational purposes.
