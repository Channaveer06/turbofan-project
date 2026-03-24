# ✈️ TurboWatch — Aircraft Engine Predictive Maintenance

Django full-stack web app for predicting Remaining Useful Life (RUL) of aircraft engines using an LSTM model trained on the NASA C-MAPSS Turbofan dataset.

---

## 🏗️ Project Structure

```
turbofan_project/
├── manage.py
├── requirements.txt
│
├── turbofan_project/        ← Django config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── predictor/               ← Main app
    ├── model_utils.py       ← ML logic (LSTM + scaler)
    ├── views.py             ← Request handling
    ├── urls.py              ← Routing
    ├── turbofan_model.h5    ← Your trained model weights
    ├── scaler.pkl           ← Your fitted scaler
    └── templates/
        └── index.html       ← Premium dashboard UI
```

---

## ⚙️ Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place model files

Make sure these files are inside the `predictor/` folder:
- `turbofan_model.h5`
- `scaler.pkl`

### 3. Run the server

```bash
cd turbofan_project
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## 📌 Features

| Feature | Description |
|---|---|
| CSV Upload | Upload engine sensor CSV → get RUL prediction |
| Demo Mode | Test the UI without real data |
| Status Display | HEALTHY / WARNING / CRITICAL with color coding |
| Life Gauge | Animated progress bar showing engine life % |
| Recommendation | Actionable maintenance guidance |
| REST API | `POST /api/predict/` for programmatic access |

---

## 🌐 REST API

**Endpoint:** `POST /api/predict/`

**Request:** multipart/form-data with field `file` (CSV)

**Response:**
```json
{
  "rul": 47.3,
  "status": "WARNING",
  "recommendation": "Schedule maintenance within the next few cycles.",
  "life_percent": 37
}
```

---

## 📊 Required CSV Columns (17 features)

```
operational_setting_1, operational_setting_2,
sensor_2, sensor_3, sensor_4, sensor_6, sensor_7,
sensor_8, sensor_9, sensor_11, sensor_12, sensor_13,
sensor_14, sensor_15, sensor_17, sensor_20, sensor_21
```

Minimum **40 rows** required (one row = one cycle).

---

## 🚦 Status Logic

| RUL | Status | Action |
|---|---|---|
| > 80 cycles | 🟢 HEALTHY | Normal monitoring |
| 31–80 cycles | 🟡 WARNING | Schedule maintenance |
| ≤ 30 cycles | 🔴 CRITICAL | Immediate maintenance |

---

Built for Predictive Maintenance · NASA C-MAPSS FD001 Dataset
