#!/usr/bin/env python
"""
Create and setup pre-trained models for testing
Uses transfer learning with pre-trained ImageNet weights
"""
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import MobileNetV2, ResNet50
import numpy as np

# Create models directory
os.makedirs('models', exist_ok=True)

print("=" * 60)
print("Setting up Pre-trained Models for Medical Diagnosis")
print("=" * 60)

# Option 1: Use MobileNetV2 with transfer learning for Malaria
print("\n📥 Creating Malaria Detection Model (MobileNetV2)...")
print("   (Using pre-trained ImageNet weights)")

malaria_base = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
malaria_base.trainable = False

malaria_model = keras.Sequential([
    malaria_base,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(2, activation='softmax')  # Healthy vs Malaria
])

malaria_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

malaria_model.save('models/malaria_model.h5')
print("   ✓ Malaria model saved to models/malaria_model.h5")
print(f"   Model parameters: {malaria_model.count_params():,}")

# Option 2: Use ResNet50 with transfer learning for TB
print("\n📥 Creating TB Detection Model (ResNet50)...")
print("   (Using pre-trained ImageNet weights)")

tb_base = ResNet50(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
tb_base.trainable = False

tb_model = keras.Sequential([
    tb_base,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(2, activation='softmax')  # Healthy vs TB
])

tb_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

tb_model.save('models/tb_model.h5')
print("   ✓ TB model saved to models/tb_model.h5")
print(f"   Model parameters: {tb_model.count_params():,}")

print("\n" + "=" * 60)
print("✅ Models Setup Complete!")
print("=" * 60)
print("\n📝 Important Notes:")
print("   • These models use pre-trained ImageNet weights (transfer learning)")
print("   • They are NOT trained on medical images yet")
print("   • For production: Fine-tune these models with your medical dataset")
print("   • Current setup is for testing the application workflow")
print("\n🚀 You can now:")
print("   1. Run: python run.py")
print("   2. Open http://localhost:5000")
print("   3. Upload images for diagnosis testing")
print("=" * 60)
