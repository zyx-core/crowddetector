import cv2
import sys
import os
import numpy as np
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
    cap.release()
    if not ret:
        print("Could not read frame")
        return

    try:
        # Detect people to get realistic current positions
        detector = PersonDetector("yolov8m.pt", confidence_threshold=0.3, device="cpu")
        detections = detector.detect(frame, track=False)
        
        vis = Visualizer(show_boxes=False, show_count=True, show_fps=False, show_track_ids=False, show_confidence=False)
        
        # Scale zone for 1920x1080 roughly
        zone = [[450, 200], [1470, 200], [1470, 800], [450, 800]]
        entry_line = [(450, 200), (450, 800)]
        exit_line = [(1470, 200), (1470, 800)]
        
        trajectories = {}
        
        if len(detections) >= 2:
            bbox1 = detections[0]['bbox']
            center1 = (int((bbox1[0] + bbox1[2])/2), int((bbox1[1] + bbox1[3])/2))
            trajectories[24] = {
                "status": "active", 
                "entry": (350, center1[1]),
                "current": center1
            }
            
            bbox2 = detections[1]['bbox']
            center2 = (int((bbox2[0] + bbox2[2])/2), int((bbox2[1] + bbox2[3])/2))
            trajectories[25] = {
                "status": "active", 
                "entry": (400, center2[1] + 20),
                "current": center2
            }
        elif len(detections) == 1:
            bbox1 = detections[0]['bbox']
            center1 = (int((bbox1[0] + bbox1[2])/2), int((bbox1[1] + bbox1[3])/2))
            trajectories[24] = {
                "status": "active", 
                "entry": (350, center1[1]),
                "current": center1
            }
            
        # Add a completed trajectory passing through the zone
        trajectories[22] = {
            "status": "completed", 
            "entry": (400, 500), 
            "exit": (1500, 550)
        }
        
        count_data = {
            'current_count': 26,
            'in_room_count': 12,
            'in_count': 8,
            'out_count': 6,
            'zone': zone,
            'entry_line': entry_line,
            'exit_line': exit_line,
            'trajectories': trajectories
        }
        
        formatted_detections = []
        for d in detections:
            formatted_detections.append({
                'bbox': d['bbox'],
                'confidence': d['conf'],
                'class_id': d['class_id']
            })
            
        vis.show_boxes = True
        frame = vis.draw_detections(frame, formatted_detections)
        
        out_frame = vis.draw_count(frame, count_data)
        
        cv2.imwrite("sample_trajectory_new_video.png", out_frame)
        print("Successfully saved sample_trajectory_new_video.png")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
