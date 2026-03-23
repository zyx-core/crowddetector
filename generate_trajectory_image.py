import cv2
import sys
import os
import numpy as np
from detector import PersonDetector
from visualizer import Visualizer

def main():
    video_path = "temp_videoplayback (1).mp4"
    if not os.path.exists(video_path):
        video_path = "temp_IMG_0552.MOV"
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
        
        zone = [[150, 100], [490, 100], [490, 380], [150, 380]]
        entry_line = [(150, 100), (150, 380)]
        exit_line = [(490, 100), (490, 380)]
        
        trajectories = {}
        
        if len(detections) >= 2:
            # Fake realistic trajectories based on actual people in frame
            # Person 1: Entering the zone
            bbox1 = detections[0]['bbox']
            center1 = (int((bbox1[0] + bbox1[2])/2), int((bbox1[1] + bbox1[3])/2))
            trajectories[14] = {
                "status": "active", 
                "entry": (130, center1[1]), # entered from left
                "current": center1
            }
            
            # Person 2: Entering the zone from a different angle
            bbox2 = detections[1]['bbox']
            center2 = (int((bbox2[0] + bbox2[2])/2), int((bbox2[1] + bbox2[3])/2))
            trajectories[15] = {
                "status": "active", 
                "entry": (140, center2[1] + 20),
                "current": center2
            }
        
        # Add a completed trajectory passing through the zone
        trajectories[12] = {
            "status": "completed", 
            "entry": (130, 250), 
            "exit": (520, 280)
        }
        
        count_data = {
            'current_count': 15,
            'in_room_count': 8,
            'in_count': 5,
            'out_count': 4,
            'zone': zone,
            'entry_line': entry_line,
            'exit_line': exit_line,
            'trajectories': trajectories
        }
        
        # Include formatted detections for context
        formatted_detections = []
        for d in detections:
            formatted_detections.append({
                'bbox': d['bbox'],
                'confidence': d['conf'],
                'class_id': d['class_id']
            })
            
        # Draw detections without boxes but just IDs if we wanted to? No, user just wants movement arrows
        # Let's draw the bounding boxes as well for context, although Visualizer will draw them if show_boxes=True
        vis.show_boxes = True
        frame = vis.draw_detections(frame, formatted_detections)
        
        out_frame = vis.draw_count(frame, count_data)
        
        cv2.imwrite("sample_trajectory_output.png", out_frame)
        print("Successfully saved sample_trajectory_output.png")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
