import cv2
import numpy as np
from logger import get_logger

class PeopleCounter:
    """
    Counts people crossing a virtual line (Tripwire).
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.is_counting = True
        self.in_count = 0
        self.out_count = 0
        self.total_count = 0
        # Explicit lines extracted from zone
        self.zone = None
        self.entry_edge = "left"
        self.exit_edge = "right"
        self.entry_line = None
        self.exit_line = None
        self.counted_ins = set()
        self.counted_outs = set()
        self.in_room_count = 0
        
        # Track previous centroids for directionality: {track_id: (x, y)}
        self.previous_centroids = {}
        self.trajectories = {} # {track_id: {"entry": (x,y), "current": (x,y), "exit": (x,y), "status": "active"}}

    def set_zone_and_edges(self, zone_coords, entry_edge="left", exit_edge="right"):
        """
        Update the rectangular counting zone and edge selection.
        """
        self.zone = zone_coords
        self.entry_edge = entry_edge
        self.exit_edge = exit_edge
        
        if zone_coords and len(zone_coords) == 4:
            edges = {
                "top": [zone_coords[0], zone_coords[1]],
                "right": [zone_coords[1], zone_coords[2]],
                "bottom": [zone_coords[2], zone_coords[3]],
                "left": [zone_coords[3], zone_coords[0]]
            }
            self.entry_line = edges.get(entry_edge)
            self.exit_line = edges.get(exit_edge)
            self.logger.info(f"Counting zone updated. Entry({self.entry_edge})={self.entry_line}, Exit({self.exit_edge})={self.exit_line}")
        else:
            self.entry_line = None
            self.exit_line = None

    def start_counting(self):
        self.is_counting = True
        self.in_count = 0
        self.out_count = 0
        self.in_room_count = 0
        self.total_count = 0
        self.counted_ins.clear()
        self.counted_outs.clear()
        self.trajectories.clear()
        self.previous_centroids.clear()
        self.logger.info("Session counting started and metrics reset.")

    def stop_counting(self):
        self.is_counting = False
        self.logger.info("Session counting stopped.")
        return self.get_statistics()

    def update(self, detections, frame_shape):
        """
        Update counts based on detections crossing the line.
        """
        current_count = len(detections)
        
        # Keep line as configured
        current_centroids = {}
        
        for det in detections:
            if 'id' not in det:
                continue
                
            track_id = det['id']
            bbox = det['bbox']
            
            # Calculate centroid
            cx = int((bbox[0] + bbox[2]) / 2)
            cy = int((bbox[1] + bbox[3]) / 2)
            curr_c = (cx, cy)
            current_centroids[track_id] = curr_c
            
            if track_id not in self.trajectories:
                self.trajectories[track_id] = {"entry": curr_c, "current": curr_c, "exit": None, "status": "active"}
            else:
                self.trajectories[track_id]["current"] = curr_c
            
            if track_id in self.previous_centroids:
                prev_c = self.previous_centroids[track_id]
                
                if self.is_counting:
                    # Check crossing entry line
                    if self.entry_line and len(self.entry_line) == 2:
                        if self._intersect(prev_c, curr_c, self.entry_line[0], self.entry_line[1]):
                            if track_id not in self.counted_ins:
                                self.in_count += 1
                                self.in_room_count = max(0, self.in_count - self.out_count)
                                self.counted_ins.add(track_id)
                                self.logger.info(f"ID {track_id} crossed ENTRY line")

                    # Check crossing exit line
                    if self.exit_line and len(self.exit_line) == 2:
                        if self._intersect(prev_c, curr_c, self.exit_line[0], self.exit_line[1]):
                            if track_id not in self.counted_outs:
                                self.out_count += 1
                                self.in_room_count = max(0, self.in_count - self.out_count)
                                self.counted_outs.add(track_id)
                                self.logger.info(f"ID {track_id} crossed EXIT line")
                                self.trajectories[track_id]["exit"] = curr_c
                                self.trajectories[track_id]["status"] = "completed"
                            
            self.previous_centroids[track_id] = curr_c
            
        self.total_count = self.in_count + self.out_count
        self.in_room_count = max(0, self.in_count - self.out_count)
        
        # Cleanup
        if len(self.trajectories) > 200:
            self.trajectories = {k: v for k, v in list(self.trajectories.items())[-50:]}
        if len(self.previous_centroids) > 200:
            self.previous_centroids = {k: v for k, v in list(self.previous_centroids.items())[-100:]}
            self.counted_ins = set(list(self.counted_ins)[-100:])
            self.counted_outs = set(list(self.counted_outs)[-100:])
        
        return {
            "current_count": current_count,
            "in_count": self.in_count,
            "out_count": self.out_count,
            "total_count": self.total_count,
            "in_room_count": self.in_room_count,
            "zone": self.zone,
            "entry_line": self.entry_line,
            "exit_line": self.exit_line,
            "entry_edge": self.entry_edge,
            "exit_edge": self.exit_edge,
            "trajectories": self.trajectories
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

    def get_statistics(self):
        """Return current statistics."""
        return {
            "in_count": self.in_count,
            "out_count": self.out_count,
            "in_room_count": self.in_room_count,
            "total_count": self.total_count
        }
