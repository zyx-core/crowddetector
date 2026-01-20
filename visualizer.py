"""
Visualization module for Live Crowd Counting System.
"""

import cv2
import numpy as np
from typing import List, Optional


class Visualizer:
    """Handles visualization of detections and counts."""
    
    # Colors (BGR format)
    COLOR_BOX_TRACKED = (0, 255, 0)  # Green for tracked
    COLOR_BOX_NEW = (0, 255, 255)  # Yellow for new detections
    COLOR_TEXT = (255, 255, 255)  # White
    COLOR_BG = (0, 0, 0)  # Black
    COLOR_COUNT_BG = (0, 100, 0)  # Dark green
    
    def __init__(self, window_name: str = "Live Crowd Counting System",
                 show_boxes: bool = True, show_track_ids: bool = True,
                 show_confidence: bool = False, show_fps: bool = True,
                 show_count: bool = True, fullscreen: bool = False):
        """
        Initialize visualizer.
        
        Args:
            window_name: Name of display window
            show_boxes: Show bounding boxes
            show_track_ids: Show track IDs on boxes
            show_confidence: Show confidence scores
            show_fps: Show FPS counter
            show_count: Show people count
            fullscreen: Start in fullscreen mode
        """
        self.window_name = window_name
        self.show_boxes = show_boxes
        self.show_track_ids = show_track_ids
        self.show_confidence = show_confidence
        self.show_fps = show_fps
        self.show_count = show_count
        
        # Create window
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        if fullscreen:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def draw_detections(self, frame: np.ndarray, detections: List[dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            
        Returns:
            Frame with visualizations
        """
        if not self.show_boxes:
            return frame
        
        frame_copy = frame.copy()
        
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            # Choose color based on whether it's tracked
            has_track_id = 'track_id' in det
            color = self.COLOR_BOX_TRACKED if has_track_id else self.COLOR_BOX_NEW
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            label_parts = []
            
            if self.show_track_ids and has_track_id:
                label_parts.append(f"ID:{det['track_id']}")
            
            if self.show_confidence:
                label_parts.append(f"{det['confidence']:.2f}")
            
            # Draw label if there's content
            if label_parts:
                label = " ".join(label_parts)
                
                # Get label size
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                # Draw label background
                cv2.rectangle(
                    frame_copy,
                    (x1, y1 - label_height - baseline - 5),
                    (x1 + label_width + 5, y1),
                    color,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    frame_copy,
                    label,
                    (x1 + 2, y1 - baseline - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    self.COLOR_TEXT,
                    1
                )
        
        return frame_copy
    
    def draw_count(self, frame: np.ndarray, count: int) -> np.ndarray:
        """
        Draw people count on frame.
        
        Args:
            frame: Input frame
            count: Current people count
            
        Returns:
            Frame with count overlay
        """
        if not self.show_count:
            return frame
        
        # Prepare count text
        count_text = f"Count: {count}"
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 3
        (text_width, text_height), baseline = cv2.getTextSize(
            count_text, font, font_scale, thickness
        )
        
        # Position (top-left corner with padding)
        padding = 10
        x = padding
        y = padding + text_height
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x - 5, y - text_height - 5),
            (x + text_width + 5, y + baseline + 5),
            self.COLOR_COUNT_BG,
            -1
        )
        
        # Draw count text
        cv2.putText(
            frame,
            count_text,
            (x, y),
            font,
            font_scale,
            self.COLOR_TEXT,
            thickness
        )
        
        return frame
    
    def draw_fps(self, frame: np.ndarray, fps: float) -> np.ndarray:
        """
        Draw FPS counter on frame.
        
        Args:
            frame: Input frame
            fps: Current FPS
            
        Returns:
            Frame with FPS overlay
        """
        if not self.show_fps:
            return frame
        
        # Prepare FPS text
        fps_text = f"FPS: {fps:.1f}"
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(
            fps_text, font, font_scale, thickness
        )
        
        # Position (top-right corner with padding)
        padding = 10
        x = frame.shape[1] - text_width - padding
        y = padding + text_height
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x - 5, y - text_height - 5),
            (x + text_width + 5, y + baseline + 5),
            self.COLOR_BG,
            -1
        )
        
        # Draw FPS text
        cv2.putText(
            frame,
            fps_text,
            (x, y),
            font,
            font_scale,
            self.COLOR_TEXT,
            thickness
        )
        
        return frame
    
    def draw_status(self, frame: np.ndarray, status: str, 
                   color: tuple = (0, 255, 0)) -> np.ndarray:
        """
        Draw status message on frame.
        
        Args:
            frame: Input frame
            status: Status message
            color: Text color (BGR)
            
        Returns:
            Frame with status overlay
        """
        # Position (bottom-left corner)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        padding = 10
        
        y = frame.shape[0] - padding
        x = padding
        
        cv2.putText(
            frame,
            status,
            (x, y),
            font,
            font_scale,
            color,
            thickness
        )
        
        return frame
    
    def show(self, frame: np.ndarray, detections: List[dict], 
             count: int, fps: float, status: Optional[str] = None) -> int:
        """
        Display frame with all visualizations.
        
        Args:
            frame: Input frame
            detections: List of detections
            count: Current people count
            fps: Current FPS
            status: Optional status message
            
        Returns:
            Key code from waitKey (for handling user input)
        """
        # Draw all visualizations
        frame = self.draw_detections(frame, detections)
        frame = self.draw_count(frame, count)
        frame = self.draw_fps(frame, fps)
        
        if status:
            frame = self.draw_status(frame, status)
        
        # Show frame
        cv2.imshow(self.window_name, frame)
        
        # Wait for key press (1ms)
        return cv2.waitKey(1) & 0xFF
    
    def close(self):
        """Close visualization window."""
        cv2.destroyWindow(self.window_name)
