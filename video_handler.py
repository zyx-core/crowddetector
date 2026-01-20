"""
Video input handler for Live Crowd Counting System.
Supports webcam, RTSP streams, and video files.
"""

import cv2
import time
from typing import Optional, Tuple
import numpy as np
from logger import get_logger


class VideoHandler:
    """Handles video input from various sources."""
    
    def __init__(self, source: str = 0, target_width: int = 640, 
                 target_height: int = 480, reconnect_enabled: bool = True,
                 max_reconnect_attempts: int = 5, retry_delay: float = 2.0,
                 backoff_multiplier: float = 1.5):
        """
        Initialize video handler.
        
        Args:
            source: Video source (0 for webcam, path for file, rtsp://... for stream)
            target_width: Target frame width
            target_height: Target frame height
            reconnect_enabled: Enable auto-reconnection for streams
            max_reconnect_attempts: Maximum reconnection attempts
            retry_delay: Initial retry delay in seconds
            backoff_multiplier: Backoff multiplier for retry delay
        """
        self.source = source
        self.target_width = target_width
        self.target_height = target_height
        self.reconnect_enabled = reconnect_enabled
        self.max_reconnect_attempts = max_reconnect_attempts
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_stream = isinstance(source, str) and source.startswith('rtsp')
        self.logger = get_logger()
        
        # FPS tracking
        self.fps = 0.0
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps_update = time.time()
        
        # Connect to source
        self._connect()
    
    def _connect(self) -> bool:
        """
        Connect to video source.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to video source: {self.source}")
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open video source: {self.source}")
                return False
            
            # Get source properties
            source_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            source_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            source_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"Video source opened - Resolution: {source_width}x{source_height}, FPS: {source_fps}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to video source: {e}")
            return False
    
    def _reconnect(self) -> bool:
        """
        Attempt to reconnect to video source with exponential backoff.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        if not self.reconnect_enabled or not self.is_stream:
            return False
        
        self.logger.warning("Attempting to reconnect to video stream...")
        
        current_delay = self.retry_delay
        for attempt in range(self.max_reconnect_attempts):
            self.logger.info(f"Reconnection attempt {attempt + 1}/{self.max_reconnect_attempts}")
            
            # Release old connection
            if self.cap is not None:
                self.cap.release()
            
            # Wait before retry
            time.sleep(current_delay)
            
            # Try to reconnect
            if self._connect():
                self.logger.info("Reconnection successful!")
                return True
            
            # Increase delay with backoff
            current_delay *= self.backoff_multiplier
        
        self.logger.error("Reconnection failed after maximum attempts")
        return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from video source.
        
        Returns:
            Tuple of (success, frame)
        """
        if self.cap is None or not self.cap.isOpened():
            if self.is_stream and self.reconnect_enabled:
                if self._reconnect():
                    return self.read()
            return False, None
        
        ret, frame = self.cap.read()
        
        if not ret:
            self.logger.warning("Failed to read frame from video source")
            if self.is_stream and self.reconnect_enabled:
                if self._reconnect():
                    return self.read()
            return False, None
        
        # Resize frame if needed
        if frame.shape[1] != self.target_width or frame.shape[0] != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height))
        
        # Update FPS
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            elapsed = current_time - self.start_time
            self.fps = self.frame_count / elapsed if elapsed > 0 else 0
            self.last_fps_update = current_time
        
        return True, frame
    
    def get_fps(self) -> float:
        """
        Get current FPS.
        
        Returns:
            Current frames per second
        """
        return self.fps
    
    def is_opened(self) -> bool:
        """
        Check if video source is opened.
        
        Returns:
            True if opened, False otherwise
        """
        return self.cap is not None and self.cap.isOpened()
    
    def release(self):
        """Release video capture resources."""
        if self.cap is not None:
            self.cap.release()
            self.logger.info("Video source released")
    
    def __del__(self):
        """Destructor to ensure resources are released."""
        self.release()
