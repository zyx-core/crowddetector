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
    
    try:
        detector = PersonDetector("yolov8m.pt", confidence_threshold=0.3, device="cpu")
        vis = Visualizer(show_boxes=True, show_count=False, show_fps=False, show_track_ids=True, show_confidence=False)
        
        out_frame = None
        for i in range(5):
            ret, frame = cap.read()
            if not ret:
                break
                
            detections = detector.detect(frame, track=True)
            
            formatted_detections = []
            for d in detections:
                formatted_det = {
                    'bbox': d['bbox'],
                    'confidence': d['conf'],
                    'class_id': d['class_id']
                }
                if 'id' in d:
                    formatted_det['track_id'] = d['id']
                formatted_detections.append(formatted_det)
                
            out_frame = vis.draw_detections(frame, formatted_detections)
        
        if out_frame is not None:
            cv2.imwrite("sample_tracking_new.png", out_frame)
            print("Successfully saved sample_tracking_new.png")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
