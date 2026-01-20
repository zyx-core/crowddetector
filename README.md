# Live Crowd Counting System

A real-time AI-powered system for detecting and counting people in live video streams using YOLOv8.

## Features

- ✅ Real-time person detection using YOLOv8
- ✅ Live people counting with tracking
- ✅ Support for webcam, RTSP streams, and video files
- ✅ Configurable confidence thresholds and parameters
- ✅ Auto-reconnection for RTSP streams
- ✅ Performance monitoring and logging
- ✅ Visual display with bounding boxes and count overlay

## Requirements

- Python 3.8+
- NVIDIA GPU (recommended for ≥30 FPS, CPU also supported)
- Webcam or IP camera (optional)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd C:\Users\arsha\OneDrive\Desktop\print\yolo
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   The YOLOv8 model weights will be automatically downloaded on first run.

## Quick Start

### Webcam (Default)
```bash
python main.py
```

### Video File
```bash
python main.py --source path/to/video.mp4
```

### RTSP Stream
```bash
python main.py --source rtsp://username:password@camera_ip:port/stream
```

### Custom Configuration
```bash
python main.py --config custom_config.yaml
```

## Configuration

The system is configured via `config.yaml`. Key parameters:

### Model Settings
- `variant`: YOLOv8 model (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
- `confidence_threshold`: Detection confidence (0.0-1.0, default: 0.4)
- `device`: Device to run on (auto, cpu, cuda, 0, 1, etc.)

### Input Settings
- `source`: Video source (0 for webcam, path for file, rtsp://... for stream)
- `resolution`: Target resolution (width, height)
- `frame_skip`: Skip frames for performance (0 = process all)

### Tracking Settings
- `enabled`: Enable tracking for persistent IDs
- `max_age`: Maximum frames to keep lost tracks
- `min_hits`: Minimum detections before track confirmation

### Display Settings
- `show_boxes`: Show bounding boxes
- `show_track_ids`: Show track IDs on boxes
- `show_fps`: Show FPS counter
- `show_count`: Show people count

### Counting Settings
- `mode`: Counting mode (frame_based or track_based)
- `smoothing`: Enable count smoothing
- `smoothing_window`: Smoothing window size

## Command Line Arguments

Override configuration with command line arguments:

```bash
python main.py --source 0 --confidence 0.5 --device cuda --model yolov8s
```

Available arguments:
- `--config`: Path to configuration file
- `--source`: Video source
- `--confidence`: Confidence threshold
- `--device`: Device (cpu, cuda, 0, 1, etc.)
- `--model`: Model variant (yolov8n, yolov8s, etc.)

## Usage

### Keyboard Controls

- **ESC** or **Q**: Quit application
- **R**: Reset counter
- **S**: Show statistics in log

### Display Elements

- **Green boxes**: Tracked persons with persistent IDs
- **Yellow boxes**: New detections (if tracking disabled)
- **Top-left**: Current people count
- **Top-right**: FPS counter
- **Bottom-left**: Status messages

## Performance Optimization

### For Higher FPS:
1. Use YOLOv8n (fastest model)
2. Reduce resolution in config
3. Enable frame skipping
4. Use GPU (CUDA)
5. Enable half precision (FP16) on GPU

### For Higher Accuracy:
1. Use YOLOv8s or YOLOv8m
2. Increase resolution
3. Lower confidence threshold
4. Enable tracking
5. Disable frame skipping

## Troubleshooting

### Low FPS
- Check if GPU is being used: Look for "cuda" in logs
- Reduce resolution or enable frame skipping
- Use a smaller model (yolov8n)

### Camera Not Opening
- Check camera permissions
- Verify RTSP URL and credentials
- Try different source indices (0, 1, 2, etc.) for webcam

### Poor Detection Accuracy
- Adjust confidence threshold (try 0.3-0.6)
- Ensure adequate lighting
- Use larger model (yolov8s or yolov8m)

### Memory Issues
- Reduce resolution
- Use YOLOv8n
- Disable half precision

## Architecture

```
main.py                 # Main application orchestrator
├── config.py          # Configuration management
├── logger.py          # Logging system
├── video_handler.py   # Video input handling
├── detector.py        # YOLOv8 person detection
├── counter.py         # Counting logic
├── visualizer.py      # Display and visualization
└── utils.py           # Utility functions
```

## Logging

Logs are written to `crowd_counter.log` by default. Log level can be configured in `config.yaml`:
- DEBUG: Detailed information
- INFO: General information (default)
- WARNING: Warning messages
- ERROR: Error messages

## Performance Metrics

The system logs performance metrics every 100 frames:
- FPS (frames per second)
- Detection latency
- Active tracks
- People count

## Future Enhancements

- Entry/exit counting with ROI
- Multi-camera support
- Web dashboard
- Database integration
- Alert system (threshold-based)
- Heatmap visualization

## License

This project uses YOLOv8 from Ultralytics, which is licensed under AGPL-3.0.

## Support

For issues or questions, please check:
1. This README
2. Configuration file comments
3. Log files for error messages

## Credits

- YOLOv8: [Ultralytics](https://github.com/ultralytics/ultralytics)
- ByteTrack: Built into YOLOv8
