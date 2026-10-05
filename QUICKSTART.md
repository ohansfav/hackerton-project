# Quick Start Guide - Malaria and TB Diagnosis System

## 🚀 Quick Start (5 Minutes)

### 1. Installation

```bash
cd "c:\Users\DELL\Desktop\hackerton project"
pip install -r requirements.txt
```

### 2. Prepare Your Data

Create this directory structure:
```
data/
├── malaria/
│   ├── train/ (healthy/ and malaria/ subdirs)
│   ├── val/
│   └── test/
└── tb/
    ├── train/ (healthy/ and tb/ subdirs)
    ├── val/
    └── test/
```

### 3. Train Models (Optional)

```python
from src.trainer import train_malaria_model, train_tb_model

# Train malaria model
train_malaria_model('data/malaria/train', 'data/malaria/val', 'data/malaria/test')

# Train TB model
train_tb_model('data/tb/train', 'data/tb/val', 'data/tb/test')
```

### 4. Start Web Application

```bash
python src/app.py
```

Access at: **http://localhost:5000**

## 💻 Python API Usage

```python
from src.predictor import MedicalDiagnosisPredictor

predictor = MedicalDiagnosisPredictor()
predictor.load_malaria_model('models/malaria_model.h5')
predictor.load_tb_model('models/tb_model.h5')

# Diagnose malaria
result = predictor.diagnose_malaria('path/to/blood_slide.jpg')
print(f"Diagnosis: {result['prediction']}, Confidence: {result['confidence']:.2%}")

# Diagnose TB
result = predictor.diagnose_tb('path/to/chest_xray.jpg')
print(f"Diagnosis: {result['prediction']}, Confidence: {result['confidence']:.2%}")
```

## 🌐 API Endpoints

```bash
# Single image diagnosis
curl -X POST -F "file=@blood_slide.jpg" \
     -F "disease_type=malaria" \
     http://localhost:5000/api/diagnose

# Get model info
curl http://localhost:5000/api/model_info

# Health check
curl http://localhost:5000/api/health
```

## ⚠️ Important Medical Disclaimer

This system ASSISTS healthcare professionals but does NOT replace them:
- ✓ Provides preliminary diagnosis
- ✓ Gives second opinion
- ✗ Must verify with qualified doctors
- ✗ Always follow medical protocols

---

For more information, see README.md and DATA_PREPARATION.md
