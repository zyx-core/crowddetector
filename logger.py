"""
Logging system for Live Crowd Counting System.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class CrowdCounterLogger:
    """Custom logger for the crowd counting system."""
    
    def __init__(self, name: str = "CrowdCounter", level: str = "INFO", 
                 log_to_file: bool = True, log_file: str = "crowd_counter.log"):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_file: Log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_to_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)
    
    def log_performance(self, fps: float, count: int, latency: float):
        """
        Log performance metrics.
        
        Args:
            fps: Frames per second
            count: Current people count
            latency: Processing latency in milliseconds
        """
        self.logger.info(f"Performance - FPS: {fps:.2f}, Count: {count}, Latency: {latency:.2f}ms")
    
    def log_detection(self, detections: int, tracks: int):
        """
        Log detection statistics.
        
        Args:
            detections: Number of detections in current frame
            tracks: Number of active tracks
        """
        self.logger.debug(f"Detection - Detections: {detections}, Active Tracks: {tracks}")


def get_logger(name: str = "CrowdCounter", level: str = "INFO",
               log_to_file: bool = True, log_file: str = "crowd_counter.log") -> CrowdCounterLogger:
    """
    Get or create logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        log_to_file: Whether to log to file
        log_file: Log file path
        
    Returns:
        CrowdCounterLogger instance
    """
    return CrowdCounterLogger(name, level, log_to_file, log_file)
