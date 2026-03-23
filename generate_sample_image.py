import cv2
import sys
import os
from detector import PersonDetector
from visualizer import Visualizer

def main():
    video_path = r"C:\Users\arsha\Downloads\11972603_1920_1080_30fps.mp4"
    if not os.path.exists(video_path):
        print("No video found.")
        return

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 50)
    ret, frame = cap.read()
    if not ret:
        print("Could not read frame")
        return

    try:
        detector = PersonDetector("yolov8m.pt", confidence_threshold=0.3, device="cpu")
        detections = detector.detect(frame, track=False)
        
        formatted_detections = []
        for d in detections:
            formatted_detections.append({
                'bbox': d['bbox'],
                'confidence': d['conf'],
                'class_id': d['class_id']
            })
            
        vis = Visualizer(show_boxes=True, show_count=False, show_fps=False, show_track_ids=False, show_confidence=True)
        out_frame = vis.draw_detections(frame, formatted_detections)
        
        cv2.imwrite("sample_detection_new.png", out_frame)
        print("Successfully saved sample_detection_new.png")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
