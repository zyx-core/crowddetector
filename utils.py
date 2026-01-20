"""
Utility functions for Live Crowd Counting System.
"""

import cv2
import time
import numpy as np
from typing import Tuple, Optional


class FPSCalculator:
    """Calculate FPS with moving average."""
    
    def __init__(self, window_size: int = 30):
        """
        Initialize FPS calculator.
        
        Args:
            window_size: Number of frames for moving average
        """
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self) -> float:
        """
        Update FPS calculation.
        
        Returns:
            Current FPS
        """
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        return fps


class PerformanceProfiler:
    """Profile performance of different components."""
    
    def __init__(self):
        """Initialize profiler."""
        self.timings = {}
        self.start_times = {}
    
    def start(self, name: str):
        """
        Start timing a component.
        
        Args:
            name: Component name
        """
        self.start_times[name] = time.time()
    
    def end(self, name: str) -> float:
        """
        End timing a component.
        
        Args:
            name: Component name
            
        Returns:
            Elapsed time in milliseconds
        """
        if name not in self.start_times:
            return 0.0
        
        elapsed = (time.time() - self.start_times[name]) * 1000  # Convert to ms
        
        if name not in self.timings:
            self.timings[name] = []
        
        self.timings[name].append(elapsed)
        
        return elapsed
    
    def get_average(self, name: str) -> float:
        """
        Get average time for a component.
        
        Args:
            name: Component name
            
        Returns:
            Average time in milliseconds
        """
        if name not in self.timings or len(self.timings[name]) == 0:
            return 0.0
        
        return sum(self.timings[name]) / len(self.timings[name])
    
    def get_report(self) -> dict:
        """
        Get performance report.
        
        Returns:
            Dictionary with timing statistics
        """
        report = {}
        for name, times in self.timings.items():
            if len(times) > 0:
                report[name] = {
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        return report


def resize_with_aspect_ratio(image: np.ndarray, width: Optional[int] = None,
                             height: Optional[int] = None) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio.
    
    Args:
        image: Input image
        width: Target width (if None, calculated from height)
        height: Target height (if None, calculated from width)
        
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    if width is None and height is None:
        return image
    
    if width is None:
        ratio = height / h
        width = int(w * ratio)
    elif height is None:
        ratio = width / w
        height = int(h * ratio)
    
    return cv2.resize(image, (width, height))


def draw_roi(frame: np.ndarray, window_name: str = "Select ROI") -> Tuple[int, int, int, int]:
    """
    Interactive ROI selection tool.
    
    Args:
        frame: Input frame
        window_name: Window name for ROI selection
        
    Returns:
        ROI coordinates (x, y, width, height)
    """
    roi = cv2.selectROI(window_name, frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow(window_name)
    return roi


class VideoWriter:
    """Write processed video to file."""
    
    def __init__(self, output_path: str, fps: float, frame_size: Tuple[int, int],
                 codec: str = 'mp4v'):
        """
        Initialize video writer.
        
        Args:
            output_path: Output video path
            fps: Frames per second
            frame_size: Frame size (width, height)
            codec: Video codec
        """
        self.output_path = output_path
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    
    def write(self, frame: np.ndarray):
        """
        Write frame to video.
        
        Args:
            frame: Frame to write
        """
        self.writer.write(frame)
    
    def release(self):
        """Release video writer."""
        self.writer.release()
    
    def __del__(self):
        """Destructor to ensure resources are released."""
        self.release()


def draw_text_with_background(img, text, x, y, font_scale=0.6, thickness=1, text_color=(255, 255, 255),
                              bg_color=(0, 0, 0), padding=5):
    """
    Draw text with a background rectangle.
    
    Args:
        img: Input image
        text: Text to draw
        x: X-coordinate
        y: Y-coordinate
        font_scale: Font scale
        thickness: Thickness
        text_color: Text color
        bg_color: Background color
        padding: Padding
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    cv2.rectangle(img, (x - padding, y - padding - text_height), 
                  (x + text_width + padding, y + padding), bg_color, -1)
    
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
