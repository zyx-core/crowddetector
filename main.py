"""
Live Crowd Counting System - Main Application
Real-time people detection and counting using YOLOv8
"""

import argparse
import signal
import sys
import time
from pathlib import Path

from config import load_config, Config
from logger import get_logger
from video_handler import VideoHandler
from detector import PersonDetector
from counter import PeopleCounter
from visualizer import Visualizer
from utils import PerformanceProfiler


class CrowdCountingSystem:
    """Main crowd counting system."""
    
    def __init__(self, config: Config):
        """
        Initialize crowd counting system.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(
            level=config.logging.level,
            log_to_file=config.logging.log_to_file,
            log_file=config.logging.log_file
        )
        
        self.running = False
        self.profiler = PerformanceProfiler()
        
        # Initialize components
        self.logger.info("Initializing Live Crowd Counting System...")
        
        try:
            # Video handler
            self.video_handler = VideoHandler(
                source=config.input.source,
                target_width=config.input.resolution['width'],
                target_height=config.input.resolution['height'],
                reconnect_enabled=config.reconnection.enabled,
                max_reconnect_attempts=config.reconnection.max_attempts,
                retry_delay=config.reconnection.retry_delay,
                backoff_multiplier=config.reconnection.backoff_multiplier
            )
            
            # Detector
            self.detector = PersonDetector(
                model_variant=config.model.variant,
                confidence_threshold=config.model.confidence_threshold,
                device=config.model.device,
                iou_threshold=config.model.iou_threshold,
                half_precision=config.performance.half_precision,
                adaptive_confidence=config.model.adaptive_confidence
            )
            
            # Counter
            self.counter = PeopleCounter(
                mode=config.counting.mode,
                smoothing=config.counting.smoothing,
                smoothing_window=config.counting.smoothing_window
            )
            
            # Visualizer
            self.visualizer = Visualizer(
                window_name=config.display.window_name,
                show_boxes=config.display.show_boxes,
                show_track_ids=config.display.show_track_ids,
                show_confidence=config.display.show_confidence,
                show_fps=config.display.show_fps,
                show_count=config.display.show_count,
                fullscreen=config.display.fullscreen
            )
            
            self.logger.info("System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing system: {e}")
            raise
    
    def run(self):
        """Run the crowd counting system."""
        self.running = True
        self.logger.info("Starting crowd counting system...")
        
        frame_count = 0
        skip_counter = 0
        
        try:
            while self.running:
                # Read frame
                self.profiler.start('frame_read')
                ret, frame = self.video_handler.read()
                self.profiler.end('frame_read')
                
                if not ret or frame is None:
                    self.logger.warning("Failed to read frame, stopping...")
                    break
                
                # Frame skipping
                if self.config.input.frame_skip > 0:
                    skip_counter += 1
                    if skip_counter <= self.config.input.frame_skip:
                        continue
                    skip_counter = 0
                
                # Detection
                self.profiler.start('detection')
                detections = self.detector.detect(
                    frame,
                    track=self.config.tracking.enabled
                )
                detection_time = self.profiler.end('detection')
                
                # Counting
                self.profiler.start('counting')
                count = self.counter.update(detections)
                self.profiler.end('counting')
                
                # Get FPS
                fps = self.video_handler.get_fps()
                
                # Visualization
                self.profiler.start('visualization')
                key = self.visualizer.show(frame, detections, count, fps)
                self.profiler.end('visualization')
                
                # Handle key press
                if key == 27 or key == ord('q'):  # ESC or 'q'
                    self.logger.info("User requested exit")
                    break
                elif key == ord('r'):  # Reset counter
                    self.counter.reset()
                    self.logger.info("Counter reset by user")
                elif key == ord('s'):  # Show statistics
                    stats = self.counter.get_statistics()
                    self.logger.info(f"Statistics: {stats}")
                
                # Log performance periodically
                frame_count += 1
                if frame_count % 100 == 0:
                    self.logger.log_performance(fps, count, detection_time)
                    self.logger.log_detection(len(detections), len(self.counter.active_track_ids))
            
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up resources...")
        
        # Print final statistics
        stats = self.counter.get_statistics()
        self.logger.info(f"Final Statistics: {stats}")
        
        # Print performance report
        perf_report = self.profiler.get_report()
        self.logger.info("Performance Report:")
        for component, metrics in perf_report.items():
            self.logger.info(f"  {component}: avg={metrics['average']:.2f}ms, "
                           f"min={metrics['min']:.2f}ms, max={metrics['max']:.2f}ms")
        
        # Release resources
        self.video_handler.release()
        self.visualizer.close()
        
        self.logger.info("Cleanup complete")
    
    def stop(self):
        """Stop the system."""
        self.running = False


def signal_handler(sig, frame):
    """Handle interrupt signals."""
    print("\nInterrupt received, shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Live Crowd Counting System using YOLOv8"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--source',
        type=str,
        help='Video source (overrides config)'
    )
    parser.add_argument(
        '--confidence',
        type=float,
        help='Confidence threshold (overrides config)'
    )
    parser.add_argument(
        '--device',
        type=str,
        help='Device to run on (overrides config)'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Model variant (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = args.config if Path(args.config).exists() else None
    config = load_config(config_path)
    
    # Override with command line arguments
    if args.source is not None:
        # Try to convert to int for webcam
        try:
            config.input.source = int(args.source)
        except ValueError:
            config.input.source = args.source
    
    if args.confidence is not None:
        config.model.confidence_threshold = args.confidence
    
    if args.device is not None:
        config.model.device = args.device
    
    if args.model is not None:
        config.model.variant = args.model
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run system
    try:
        system = CrowdCountingSystem(config)
        system.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
