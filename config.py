"""
Configuration management for Live Crowd Counting System.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class ModelConfig:
    """Model configuration settings."""
    variant: str = "yolov8m"
    confidence_threshold: float = 0.4
    device: str = "auto"
    iou_threshold: float = 0.45
    adaptive_confidence: Optional[dict] = None # Deprecated, kept for safety or removed? I'll replace it.
    mode_1: Optional[dict] = None
    mode_2: Optional[dict] = None
    hybrid: Optional[dict] = None

    def __post_init__(self):
        """Validate configuration."""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.iou_threshold <= 1.0:
            raise ValueError("iou_threshold must be between 0.0 and 1.0")


@dataclass
class InputConfig:
    """Input source configuration."""
    source: Union[int, str] = 0
    resolution: dict = field(default_factory=lambda: {"width": 640, "height": 480})
    target_fps: int = 30
    frame_skip: int = 0

    def __post_init__(self):
        """Validate configuration."""
        if self.frame_skip < 0:
            raise ValueError("frame_skip must be non-negative")
        if self.target_fps <= 0:
            raise ValueError("target_fps must be positive")


@dataclass
class TrackingConfig:
    """Tracking configuration settings."""
    enabled: bool = True
    tracker: str = "bytetrack.yaml"
    max_age: int = 30
    min_hits: int = 3
    iou_threshold: float = 0.3

    def __post_init__(self):
        """Validate configuration."""
        if self.max_age < 1:
            raise ValueError("max_age must be at least 1")
        if self.min_hits < 1:
            raise ValueError("min_hits must be at least 1")


@dataclass
class DisplayConfig:
    """Display configuration settings."""
    show_boxes: bool = True
    show_track_ids: bool = True
    show_confidence: bool = False
    show_fps: bool = True
    show_count: bool = True
    fullscreen: bool = False
    window_name: str = "Live Crowd Counting System"


@dataclass
class CountingConfig:
    """Counting configuration settings."""
    mode: str = "track_based"  # frame_based or track_based
    smoothing: bool = True
    smoothing_window: int = 5
    counting_zone: Optional[list] = None
    entry_edge: str = "left"
    exit_edge: str = "right"

    def __post_init__(self):
        """Validate configuration."""
        if self.mode not in ["frame_based", "track_based"]:
            raise ValueError("mode must be 'frame_based' or 'track_based'")
        if self.smoothing_window < 1:
            raise ValueError("smoothing_window must be at least 1")


@dataclass
class PerformanceConfig:
    """Performance optimization settings."""
    batch_size: int = 1
    half_precision: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    log_to_file: bool = True
    log_file: str = "crowd_counter.log"

    def __post_init__(self):
        """Validate configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"level must be one of {valid_levels}")


@dataclass
class ReconnectionConfig:
    """Reconnection settings for RTSP streams."""
    enabled: bool = True
    max_attempts: int = 5
    retry_delay: float = 2.0
    backoff_multiplier: float = 1.5

    def __post_init__(self):
        """Validate configuration."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")


@dataclass
class Config:
    """Main configuration class."""
    model: ModelConfig = field(default_factory=ModelConfig)
    input: InputConfig = field(default_factory=InputConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    counting: CountingConfig = field(default_factory=CountingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    reconnection: ReconnectionConfig = field(default_factory=ReconnectionConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """Load configuration from YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls(
            model=ModelConfig(**config_dict.get('model', {})),
            input=InputConfig(**config_dict.get('input', {})),
            tracking=TrackingConfig(**config_dict.get('tracking', {})),
            display=DisplayConfig(**config_dict.get('display', {})),
            counting=CountingConfig(**config_dict.get('counting', {})),
            performance=PerformanceConfig(**config_dict.get('performance', {})),
            logging=LoggingConfig(**config_dict.get('logging', {})),
            reconnection=ReconnectionConfig(**config_dict.get('reconnection', {}))
        )

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'Config':
        """Load configuration from dictionary."""
        return cls(
            model=ModelConfig(**config_dict.get('model', {})),
            input=InputConfig(**config_dict.get('input', {})),
            tracking=TrackingConfig(**config_dict.get('tracking', {})),
            display=DisplayConfig(**config_dict.get('display', {})),
            counting=CountingConfig(**config_dict.get('counting', {})),
            performance=PerformanceConfig(**config_dict.get('performance', {})),
            logging=LoggingConfig(**config_dict.get('logging', {})),
            reconnection=ReconnectionConfig(**config_dict.get('reconnection', {}))
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'model': self.model.__dict__,
            'input': self.input.__dict__,
            'tracking': self.tracking.__dict__,
            'display': self.display.__dict__,
            'counting': self.counting.__dict__,
            'performance': self.performance.__dict__,
            'logging': self.logging.__dict__,
            'reconnection': self.reconnection.__dict__
        }

    def save_yaml(self, yaml_path: str):
        """Save configuration to YAML file."""
        with open(yaml_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or create default.
    
    Args:
        config_path: Path to YAML configuration file. If None, uses default config.
        
    Returns:
        Config object
    """
    if config_path and os.path.exists(config_path):
        return Config.from_yaml(config_path)
    elif config_path:
        print(f"Warning: Config file {config_path} not found. Using default configuration.")
    
    return Config()
