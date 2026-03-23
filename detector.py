"""
YOLOv8 detector for person detection.
"""

import torch
from ultralytics import YOLO
from typing import List, Tuple
import numpy as np
from logger import get_logger


class PersonDetector:
    """YOLOv8-based person detector."""
    
    # COCO class ID for person
    PERSON_CLASS_ID = 0
    
    def __init__(self, model_variant: str = "yolov8m", confidence_threshold: float = 0.4,
                 device: str = "auto", iou_threshold: float = 0.45, 
                 half_precision: bool = False, adaptive_confidence: dict = None):
        """
        Initialize person detector.
        
        Args:
            model_variant: YOLOv8 model variant (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
            confidence_threshold: Base confidence threshold for detections
            device: Device to run inference on (auto, cpu, cuda, 0, 1, etc.)
            iou_threshold: IOU threshold for NMS
            half_precision: Use FP16 for faster inference (requires GPU)
            adaptive_confidence: Dict with adaptive confidence settings
        """
        self.model_variant = model_variant
        self.base_confidence_threshold = confidence_threshold
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.half_precision = half_precision
        self.logger = get_logger()

        
        # Track previous detection count for density estimation
        self.previous_detection_count = 0
        
        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.logger.info(f"Initializing {model_variant} on {self.device}")
        
        # Load model
        try:
            if model_variant.endswith(".pt"):
                model_name = model_variant
            else:
                model_name = f"{model_variant}.pt"
                
            self.model = YOLO(model_name)
            
            # Move to device
            self.model.to(self.device)
            
            # Enable half precision if requested and on GPU
            if half_precision and self.device != "cpu":
                self.model.half()
                self.logger.info("Half precision (FP16) enabled")
            
            self.logger.info(f"Model {model_variant} loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    def detect(self, frame: np.ndarray, track: bool = False) -> List[dict]:
        """
        Detect persons in frame using YOLOv8 (Mode 1).
        
        Args:
            frame: Input frame (BGR format)
            track: Whether to use tracking
            
        Returns:
            List of dictionaries with 'bbox', 'conf', 'class_id', and optional 'id'
        """
        try:
            # Run inference
            if track:
                results = self.model.track(
                    frame,
                    conf=0.25, # Lowered confidence to pick up distant people
                    iou=self.iou_threshold,
                    classes=[self.PERSON_CLASS_ID],
                    persist=True,
                    tracker="botsort.yaml",
                    verbose=False,
                    imgsz=1088 # Increased inference resolution explicitly for 1080p 'small heads'
                )
            else:
                results = self.model(
                    frame,
                    conf=0.25, 
                    iou=self.iou_threshold,
                    classes=[self.PERSON_CLASS_ID],
                    verbose=False,
                    imgsz=1088
                )
            
            # Parse results
            detections = []
            
            if len(results) > 0:
                result = results[0]
                
                # Get boxes
                boxes = result.boxes
                
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        
                        det = {
                            'bbox': [x1, y1, x2, y2],
                            'conf': conf,
                            'class_id': cls
                        }
                        
                        # Add track ID if available
                        if box.id is not None:
                            det['id'] = int(box.id[0].cpu().numpy())
                            
                        detections.append(det)
                        
            return detections
            
        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            return []
    
    def get_model_info(self) -> dict:
        """
        Get model information.
        
        Returns:
            Dictionary with model info
        """
        return {
            'variant': self.model_variant,
            'device': self.device,
            'confidence_threshold': self.confidence_threshold,
            'iou_threshold': self.iou_threshold,
            'half_precision': self.half_precision
        }
