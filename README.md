# Malaria and Tuberculosis (TB) Diagnosis System

## 🏥 Project Overview

An AI-powered medical image analysis system that assists local healthcare workers in preliminary diagnosis of:
- **Malaria**: Blood slide image analysis for parasite detection
- **Tuberculosis (TB)**: Chest X-ray analysis for TB detection

This system provides rapid, automated second opinions crucial in areas with shortage of medical specialists.

## 🎯 Key Features

- **Dual Disease Detection**: Malaria (blood slides) and TB (chest X-rays)
- **High Accuracy**: Deep learning models trained on medical datasets
- **User-Friendly Interface**: Web-based application for easy access
- **Real-time Analysis**: Fast inference for quick diagnosis assistance
- **Confidence Scores**: Model provides confidence levels for each prediction
- **Image Preprocessing**: Automatic image enhancement and normalization
- **Batch Processing**: Analyze multiple images at once
- **Local Deployment**: Can run on local healthcare infrastructure

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip or conda

### Installation

1. Navigate to the project directory:
```bash
cd "c:\Users\DELL\Desktop\hackerton project"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask web application:
```bash
python src/app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
hackerton project/
├── src/
│   ├── app.py                 # Flask web application
│   ├── model_builder.py       # Model architecture and training
│   ├── image_processor.py     # Image preprocessing utilities
│   ├── predictor.py           # Inference engine
│   ├── trainer.py             # Training pipeline
│   ├── utils.py               # Helper utilities
│   └── __init__.py
├── data/
│   ├── malaria/
│   │   ├── train/
│   │   ├── test/
│   │   └── val/
│   └── tb/
│       ├── train/
│       ├── test/
│       └── val/
├── models/                     # Trained model weights
├── tests/
│   └── test_models.py         # Unit tests
├── config.yaml                 # Configuration file
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

## 🔧 Configuration

Edit `config.yaml` to configure:
- Model paths
- Image dimensions
- Confidence thresholds
- Training parameters
- API settings

## 🎓 Training

To train models with your own data:

```bash
python src/trainer.py --disease malaria --data-path data/malaria
python src/trainer.py --disease tb --data-path data/tb
```

## 🔍 Usage Examples

### Python API
```python
from src.predictor import MedicalDiagnosisPredictor

predictor = MedicalDiagnosisPredictor()

# Malaria diagnosis
result = predictor.diagnose_malaria('path/to/blood_slide.jpg')
print(f"Diagnosis: {result['prediction']}, Confidence: {result['confidence']}")

# TB diagnosis
result = predictor.diagnose_tb('path/to/chest_xray.jpg')
print(f"Diagnosis: {result['prediction']}, Confidence: {result['confidence']}")
```

### Web Interface
1. Upload an image (JPG, PNG)
2. Select disease type (Malaria/TB)
3. Click "Analyze"
4. View results with confidence scores

## ⚠️ Medical Disclaimer

**This system is designed to ASSIST healthcare professionals, not replace them.**
- Results should always be verified by qualified medical professionals
- System provides a second opinion only
- Always follow local medical protocols and guidelines
- This tool is meant for preliminary screening assistance

## 📞 Support

For issues or questions, please refer to the documentation files or check the logs directory.

---

**Created**: November 20, 2025
**Status**: Production Ready
