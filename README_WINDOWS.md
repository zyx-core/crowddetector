# CrowdSense - Windows Desktop Application

## 🎯 What is This?

A standalone Windows application for real-time face detection and crowd counting. No installation of Python or dependencies required!

## 📦 Installation

### Option 1: Download Pre-built Executable (Recommended)

1. Download `CrowdSense-Windows.zip` from releases
2. Extract to any folder (e.g., `C:\CrowdSense`)
3. Double-click `CrowdSense.exe`
4. Browser opens automatically at http://localhost:8000

### Option 2: Build from Source

**Requirements:**
- Python 3.11+
- CUDA-capable GPU (optional, for faster inference)

**Steps:**

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Build executable
pyinstaller crowdsense.spec

# 3. Find output in dist/CrowdSense/
```

## 🚀 Usage

1. **Launch App:** Double-click `CrowdSense.exe`
2. **Wait for Browser:** Opens automatically in ~5 seconds
3. **Select Mode:**
   - **Auto Mode:** Switches between tracking and heatmap automatically
   - **Tracking Mode:** Shows bounding boxes and tripwire
   - **Surge Mode:** Shows density heatmap and flow

4. **Choose Input:**
   - **Image:** Upload a photo for detection
   - **Video:** Upload a video file
   - **Webcam:** Use your computer's camera

## 📊 Features

✅ Real-time face detection (custom YOLOv8n model)  
✅ Bidirectional counting (IN/OUT tracking)  
✅ Interactive tripwire editor  
✅ Live count graphs (60-second history)  
✅ CSV data export  
✅ Optical flow visualization  
✅ Offline operation (no internet required)

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
model:
  variant: "best.pt"
  confidence_threshold: 0.4
  device: "auto"  # auto, cpu, cuda

hybrid:
  switch_thresholds:
    confidence_drop: 0.60
    overlap_iou: 0.3
  recovery_threshold: 5
```

## 📁 File Structure

```
CrowdSense/
├── CrowdSense.exe          # Main executable
├── best.pt                 # Trained face detection model
├── config.yaml             # Configuration file
├── web/                    # UI files
│   ├── index.html
│   ├── app.js
│   └── style.css
└── _internal/              # Python runtime & dependencies
```

## 💾 System Requirements

**Minimum:**
- Windows 10/11 (64-bit)
- 4GB RAM
- 500MB disk space
- Intel/AMD CPU

**Recommended:**
- Windows 11
- 8GB+ RAM
- NVIDIA GPU (for real-time performance)
- Webcam (for live detection)

## 🐛 Troubleshooting

### App Won't Start
- **Check antivirus:** Windows Defender may block unsigned .exe files
- **Run as Administrator:** Right-click → "Run as administrator"
- **Check port 8000:** Make sure no other app is using it

### Slow Performance
- **Use GPU:** Ensure CUDA is installed for NVIDIA GPUs
- **Lower resolution:** Edit `config.yaml` → `input.resolution`
- **Close other apps:** Free up RAM

### Browser Doesn't Open
- Manually open: http://localhost:8000
- Check firewall settings

## 📝 License

MIT License - See LICENSE file

## 🙏 Credits

- **YOLOv8:** Ultralytics
- **Model Training:** WIDER FACE dataset
- **UI Framework:** Vanilla JS + Chart.js

## 📧 Support

For issues or questions:
- GitHub: [zyx-core/crowddetector](https://github.com/zyx-core/crowddetector)
- Email: ershadpersonal123@gmail.com

---

**Version:** 1.0.0  
**Build Date:** 2026-01-20  
**Model:** YOLOv8n (WIDER FACE)
