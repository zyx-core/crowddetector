import numpy as np
from detector import PersonDetector
from config import load_config
from density_estimator import DensityEstimator
from counter import PeopleCounter

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
        
        # Mode 2 Engine
        self.density_estimator = DensityEstimator()
        
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

    def update_tripwire(self, line_coords):
        """Update the tripwire line in the counter."""
        if self.counter:
            self.counter.set_line(line_coords)

    def process_frame(self, frame):
        """
        Process frame and decide mode.
        """
        detections = self.detector.detect(frame, track=True)
        
        avg_conf = 0
        high_overlap_count = 0
        
        if len(detections) > 0:
            avg_conf = np.mean([d['conf'] for d in detections])
            high_overlap_count = self._count_high_overlaps(detections)
            
        print(f"DEBUG: Mode={self.current_mode} Count={len(detections)} AvgConf={avg_conf:.2f} Overlaps={high_overlap_count}")
            
        # Switch Logic
        if self.manual_override is None:
            if self.current_mode == self.MODE_1:
                # Check triggers to switch to Mode 2
                if (len(detections) > 0 and avg_conf < self.conf_drop_threshold) or \
                   high_overlap_count > 0: # Sensitivity tuned
                    self.current_mode = self.MODE_2
                    print(f"Switched to MODE 2 (Surge): Avg Conf {avg_conf:.2f}, Overlaps {high_overlap_count}")
                    
            elif self.current_mode == self.MODE_2:
                # Check triggers to revert to Mode 1 (Recovery)
                if len(detections) < self.recovery_threshold:
                    self.current_mode = self.MODE_1
                    print(f"Switched to MODE 1 (Tracking): Count {len(detections)}")
                
        heatmap = None
        count = len(detections)
        count_data = {"in_count": 0, "out_count": 0, "line": None}
        
        if self.current_mode == self.MODE_2:
             # Generate Heatmap
             heatmap, density_sum = self.density_estimator.generate_heatmap(frame, detections)
        else:
             # Mode 1: Update Counter
             count_data = self.counter.update(detections, frame.shape)
                 
        return {
            "mode": self.current_mode,
            "detections": detections, 
            "count": count,
            "heatmap": heatmap,
            "counts": count_data # New field for IN/OUT
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
