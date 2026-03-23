import cv2
import sys
import os
import numpy as np
import yaml
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
        print("Could not read frame.")
        return

    try:
        vis = Visualizer(show_boxes=False, show_count=True, show_fps=False, show_track_ids=False, show_confidence=False)
        
        # Scale zone for 1920x1080
        zone = [[450, 200], [1470, 200], [1470, 800], [450, 800]]
        
        count_data = {
            'current_count': 26, # Example counts representing the crowd in this specific frame
            'in_room_count': 12,
            'in_count': 8,
            'out_count': 6,
            'zone': zone
        }
        
        out_frame = vis.draw_count(frame, count_data)
        
        cv2.imwrite("sample_counting_zone_new.png", out_frame)
        print("Successfully saved sample_counting_zone_new.png")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
