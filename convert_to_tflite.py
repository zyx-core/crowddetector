"""
Convert YOLOv8 model to TensorFlow Lite for mobile deployment.
Run this script to create best.tflite from best.pt
"""

from ultralytics import YOLO
import os

def convert_to_tflite():
    print("🔄 Loading YOLOv8 model...")
    model = YOLO('best.pt')
    
    print("📦 Exporting to TensorFlow Lite...")
    # Export with INT8 quantization for smaller size and faster inference
    model.export(
        format='tflite',
        imgsz=640,
        int8=True,  # Quantize to 8-bit integers
        optimize=True
    )
    
    print("✅ Conversion complete!")
    print("📁 Output: best.tflite")
    
    # Check file sizes
    pt_size = os.path.getsize('best.pt') / (1024 * 1024)
    tflite_size = os.path.getsize('best_saved_model/best_int8.tflite') / (1024 * 1024)
    
    print(f"\n📊 Size Comparison:")
    print(f"   Original (.pt):  {pt_size:.2f} MB")
    print(f"   TFLite (int8):   {tflite_size:.2f} MB")
    print(f"   Reduction:       {((pt_size - tflite_size) / pt_size * 100):.1f}%")

if __name__ == "__main__":
    convert_to_tflite()
