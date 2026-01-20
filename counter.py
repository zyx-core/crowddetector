import cv2
import numpy as np
from logger import get_logger

class PeopleCounter:
    """
    Counts people crossing a virtual line (Tripwire).
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.in_count = 0
        self.out_count = 0
        self.total_count = 0
        
        # Tripwire Line: (x1, y1), (x2, y2)
        # Default: Horizontal line in the middle (will be updated on first frame)
        self.line = [(0, 240), (640, 240)] 
        
        # Track previous centroids for directionality: {track_id: (x, y)}
        self.previous_centroids = {}
        
        # Track side state: {track_id: "UP" | "DOWN"}
        # Assumes y=0 is top. Line is horizontal.
        # DOWN (y > line_y) = IN
        # UP (y < line_y) = OUT
        self.object_states = {}
    def set_line(self, line_coords):
        """
        Update the tripwire line coordinates.
        line_coords: [(x1, y1), (x2, y2)]
        """
        self.line = line_coords
        self.logger.info(f"Tripwire updated: {self.line}")

    def update(self, detections, frame_shape):
        """
        Update counts based on detections crossing the line.
        """
        current_count = len(detections)
        
        # Update line details if frame size changed or not set (Dynamic)
        h, w = frame_shape[:2]
        if self.line[1][0] != w:
             y_line = int(h * 0.6)
             self.line = [(0, y_line), (w, y_line)]
             
        line_y = self.line[0][1]
        
        current_centroids = {}
        
        for det in detections:
            if 'id' not in det:
                continue
                
            track_id = det['id']
            bbox = det['bbox']
            
            # Calculate centroid
            cx = int((bbox[0] + bbox[2]) / 2)
            cy = int((bbox[1] + bbox[3]) / 2)
            
            current_centroids[track_id] = (cx, cy)
            
            # Determine current side
            current_side = "DOWN" if cy > line_y else "UP"
            
            # Check for crossing based on state change
            if track_id in self.object_states:
                prev_side = self.object_states[track_id]
                
                if prev_side != current_side:
                    # CROSSING DETECTED
                    if prev_side == "UP" and current_side == "DOWN":
                        self.in_count += 1
                        self.logger.info(f"ID {track_id} crossed IN")
                    elif prev_side == "DOWN" and current_side == "UP":
                        self.out_count += 1
                        self.logger.info(f"ID {track_id} crossed OUT")
                    
                    self.total_count = self.in_count + self.out_count
            
            # Update state
            self.object_states[track_id] = current_side
        
        # Cleanup (Optional: remove old IDs from object_states to save memory)
        # self.previous_centroids = current_centroids # Not strictly needed for side-state logic but good for vectors
        
        return {
            "current_count": current_count,
            "in_count": self.in_count,
            "out_count": self.out_count,
            "total_count": self.total_count,
            "line": self.line
        }
        
    def _intersect(self, A, B, C, D):
        """Return true if line segments AB and CD intersect"""
        return self._ccw(A,C,D) != self._ccw(B,C,D) and self._ccw(A,B,C) != self._ccw(A,B,D)

    def _ccw(self, A, B, C):
        """Check for counter-clockwise orientation"""
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        
    def _get_direction(self, p1, p2):
        """
        Simple direction check based on Y movement relative to line.
        """
        if p2[1] > p1[1]:
            return "IN"
        return "OUT"
