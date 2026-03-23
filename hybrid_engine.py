import numpy as np
from detector import PersonDetector
from config import load_config
from density_estimator import DensityEstimator
from counter import PeopleCounter
from optical_flow import OpticalFlowCalculator

class HybridEngine:
    """
    Manages switching between Mode 1 (Individual Tracking) and Mode 2 (Surge Estimation).
    """
    
    MODE_1 = "INDIVIDUAL_TRACKING"
    MODE_2 = "SURGE_ESTIMATION"
    
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.current_mode = self.MODE_1
        
        # Mode 1 Engine
        self.detector = PersonDetector(
            model_variant=self.config.model.variant,
            confidence_threshold=self.config.model.confidence_threshold,
            device=self.config.model.device,
            iou_threshold=self.config.model.iou_threshold
        )
        self.counter = PeopleCounter()
        if hasattr(self.config.counting, 'counting_zone') and self.config.counting.counting_zone is not None:
             self.counter.set_zone_and_edges(
                 self.config.counting.counting_zone,
                 getattr(self.config.counting, 'entry_edge', 'left'),
                 getattr(self.config.counting, 'exit_edge', 'right')
             )
        
        # Mode 2 Engine
        self.density_estimator = DensityEstimator()
        self.flow_calculator = OpticalFlowCalculator()
        
        # Switching Logic Parameters
        self.conf_drop_threshold = 0.45
        self.overlap_iou_threshold = 0.6
        self.recovery_threshold = 5 
        
        if hasattr(self.config, 'hybrid'):
             self.conf_drop_threshold = self.config.hybrid['switch_thresholds']['confidence_drop']
             self.overlap_iou_threshold = self.config.hybrid['switch_thresholds']['overlap_iou']
             self.recovery_threshold = self.config.hybrid['recovery_threshold']
             
        self.manual_override = None # None, MODE_1, or MODE_2

    def set_manual_mode(self, mode):
        """Force a specific mode."""
        if mode in [self.MODE_1, self.MODE_2, "AUTO"]:
            if mode == "AUTO":
                self.manual_override = None
            else:
                self.manual_override = mode
                self.current_mode = mode
            print(f"Manual Mode Set to: {mode}")
            
    def start_counting(self):
        if self.counter:
            self.counter.start_counting()
            
    def stop_counting(self):
        if self.counter:
            return self.counter.stop_counting()
        return None

    def update_zone_and_edges(self, zone_coords, entry_edge, exit_edge):
        """Update the counting lines in the counter."""
        if self.counter:
            self.counter.set_zone_and_edges(zone_coords, entry_edge, exit_edge)

    def process_frame(self, frame):
        """
        Process frame and decide mode with refined hysteresis logic.
        """
        # Always run detection to get metrics
        detections = self.detector.detect(frame, track=True)
        count = len(detections)
        
        # Calculate metrics
        avg_conf = 0.0
        if count > 0:
            avg_conf = np.mean([d['conf'] for d in detections])
            
        high_overlap_count = self._count_high_overlaps(detections)
        
        # --- Refined Switching Logic with Hysteresis ---
        if self.manual_override is None:
            # Thresholds optimized for face detection
            CROWD_LIMIT = 25          # Force Surge if more than this
            RECOVERY_LIMIT = 10       # Switch back if less than this (hysteresis buffer)
            CONF_DROP_THRESH = self.conf_drop_threshold  # 0.60
            MIN_CROWD_FOR_CHECK = 5   # Only check confidence if crowd exists
            
            if self.current_mode == self.MODE_1:
                # Triggers for Surge Mode:
                # 1. Hard crowd limit (too many people)
                # 2. Confidence drop (faces occluded/blurry)
                # 3. High overlap (people clumping)
                
                is_crowded = count > CROWD_LIMIT
                is_uncertain = (count > MIN_CROWD_FOR_CHECK) and (avg_conf < CONF_DROP_THRESH)
                is_clumping = high_overlap_count > 2
                
                if is_crowded or is_uncertain or is_clumping:
                    self.current_mode = self.MODE_2
                    self.flow_calculator.reset()
                    print(f"🔄 Auto Switch -> SURGE MODE")
                    print(f"   Count: {count}, Conf: {avg_conf:.2f}, Overlaps: {high_overlap_count}")
                     
            elif self.current_mode == self.MODE_2:
                # Recovery to Tracking Mode:
                # Must be sparse enough AND confident enough
                # Hysteresis: 10-25 buffer zone prevents flickering
                
                is_sparse = count < RECOVERY_LIMIT
                is_confident = (count == 0) or (avg_conf > (CONF_DROP_THRESH + 0.05))
                
                if is_sparse and is_confident:
                    self.current_mode = self.MODE_1
                    print(f"🔄 Auto Switch -> TRACKING MODE")
                    print(f"   Count: {count}, Conf: {avg_conf:.2f}")
        
        # Always Update Counter to keep IN/OUT and trajectories active
        count_data = self.counter.update(detections, frame.shape) if self.counter else {"in_count": 0, "out_count": 0, "line": None}
        
        heatmap = None
        flow_data = None
        
        if self.current_mode == self.MODE_2:
            # Generate Heatmap
            heatmap, density_sum = self.density_estimator.generate_heatmap(frame, detections)
            # Calculate Optical Flow
            flow_data = self.flow_calculator.calculate_flow(frame)
                 
        return {
            "mode": self.current_mode,
            "detections": detections, 
            "count": count,
            "heatmap": heatmap,
            "counts": count_data,
            "flow": flow_data
        }

    def _count_high_overlaps(self, detections):
        """
        Count number of boxes overlapping with IoU > threshold.
        """
        count = 0
        boxes = [d['bbox'] for d in detections]
        if not boxes:
            return 0
            
        # Basic O(N^2) check for now
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                iou = self._calculate_iou(boxes[i], boxes[j])
                if iou > self.overlap_iou_threshold:
                    count += 1
        return count

    def _calculate_iou(self, boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        # compute the area of intersection rectangle
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

        # compute the area of both the prediction and ground-truth rectangles
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

        # compute the intersection over union
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou
