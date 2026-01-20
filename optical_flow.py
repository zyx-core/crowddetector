import cv2
import numpy as np

class OpticalFlowCalculator:
    """
    Calculates optical flow to determine crowd movement direction in Surge Mode.
    Uses Farneback Dense Optical Flow.
    """
    
    def __init__(self):
        self.prev_gray = None
        self.in_flow = 0.0
        self.out_flow = 0.0
        
    def calculate_flow(self, frame):
        """
        Calculate dense optical flow between previous and current frame.
        Returns: (avg_dx, avg_dy, flow_magnitude)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Resize for performance (optical flow is expensive)
        small_gray = cv2.resize(gray, (320, 240))
        
        if self.prev_gray is None:
            self.prev_gray = small_gray
            return {"direction": "STATIONARY", "magnitude": 0}
            
        # Calculate Dense Flow (Farneback)
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, small_gray, None,
            pyr_scale=0.5, levels=3, winsize=15, 
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        # flow is (h, w, 2) -> (dy, dx) ? Check docs: (y, x, 2) usually
        # flow[..., 0] is dx (horizontal)
        # flow[..., 1] is dy (vertical)
        
        avg_dx = np.mean(flow[..., 0])
        avg_dy = np.mean(flow[..., 1])
        magnitude = np.sqrt(avg_dx**2 + avg_dy**2)
        
        # Determine Direction
        # Assuming Y+ is DOWN (IN), Y- is UP (OUT)
        direction = "STATIONARY"
        if magnitude > 0.5: # Threshold for noise
            if avg_dy > 0.2:
                direction = "IN"
                self.in_flow += magnitude # Accumulate "flow pressure"
            elif avg_dy < -0.2:
                direction = "OUT"
                self.out_flow += magnitude
                
        self.prev_gray = small_gray
        
        return {
            "direction": direction,
            "dx": avg_dx,
            "dy": avg_dy,
            "magnitude": magnitude
        }
        
    def reset(self):
        self.prev_gray = None
        self.in_flow = 0
        self.out_flow = 0
