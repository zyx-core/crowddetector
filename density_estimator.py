import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

class DensityEstimator:
    """
    Estimates density map. 
    Phase 1: Simulated using Gaussian Kernel on YOLO box centroids.
    Phase 3: Will use CSRNet.
    """
    
    def __init__(self):
        pass
        
    def generate_heatmap(self, frame, detections):
        """
        Generate density heatmap from detections.
        """
        h, w = frame.shape[:2]
        density_map = np.zeros((h, w), dtype=np.float32)
        
        for det in detections:
            bbox = det['bbox']
            # Center
            cx = int((bbox[0] + bbox[2]) / 2)
            cy = int((bbox[1] + bbox[3]) / 2)
            
            if 0 <= cx < w and 0 <= cy < h:
                density_map[cy, cx] = 1.0
                
        # Apply Gaussian Blur to creating blobs
        # Sigma depends on perspective, but fixed for now
        heatmap = gaussian_filter(density_map, sigma=15)
        
        # Normalize for visualization (0-255)
        heatmap_vis = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_vis = np.uint8(heatmap_vis)
        heatmap_color = cv2.applyColorMap(heatmap_vis, cv2.COLORMAP_JET)
        
        return heatmap_color, np.sum(heatmap)
