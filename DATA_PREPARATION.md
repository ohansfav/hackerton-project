# Data Preparation Guide

## 📋 Overview

Guide to collecting and organizing medical images for training the models.

## 🏥 Recommended Data Sources

### Malaria
- **Malaria Cell Images Dataset** (Kaggle)
  - https://www.kaggle.com/datasets/ialopez/malaria
  - 27,558 blood slide images
  - Classes: Parasitized (infected), Uninfected

### TB
- **NIH Chest X-ray Dataset** (Kaggle)
  - https://www.kaggle.com/nih-chest-xrays/data
  - 112,000+ X-ray images
- **Montgomery County X-ray Set**
  - Public dataset with TB/non-TB labels

## 📁 Directory Structure

```
data/
├── malaria/
│   ├── train/
│   │   ├── healthy/        (70% of data)
│   │   └── malaria/
│   ├── val/
│   │   ├── healthy/        (20% of data)
│   │   └── malaria/
│   └── test/
│       ├── healthy/        (10% of data)
│       └── malaria/
└── tb/
    ├── train/
    │   ├── healthy/
    │   └── tb/
    ├── val/
    │   ├── healthy/
    │   └── tb/
    └── test/
        ├── healthy/
        └── tb/
```

## 🖼️ Image Requirements

### Malaria
- Format: RGB color images
- Size: 224×224 recommended
- Minimum: 100×100 pixels
- File type: JPG, PNG

### TB
- Format: Grayscale or RGB X-rays
- Size: 224×224 recommended
- File type: PNG, JPG

## 🔐 Privacy Considerations

1. **De-identify** all patient data
2. **Ensure** proper consent and IRB approval
3. **Comply** with HIPAA/GDPR regulations
4. **Store** securely and encrypt

## 📊 Data Statistics

Recommended minimum dataset sizes:
- **Small**: 500 images per class (rapid prototyping)
- **Medium**: 2,000 images per class (good performance)
- **Large**: 10,000+ images per class (production)

---

For more information, see README.md and QUICKSTART.md
