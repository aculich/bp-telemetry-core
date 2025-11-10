"""
Instrumentation and monitoring for Blueplane Telemetry Core.
"""

import logging
import time
from functools import wraps
from typing import Callable, Any
from contextlib import contextmanager

from .config import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("blueplane")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific component."""
    return logging.getLogger(f"blueplane.{name}")


@contextmanager
def timer(operation_name: str, logger_instance: logging.Logger = None):
    """Context manager for timing operations."""
    log = logger_instance or logger
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        log.info(f"{operation_name} completed in {duration_ms:.2f}ms")


def log_execution_time(operation_name: str = None):
    """Decorator to log execution time of functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            name = operation_name or f"{func.__module__}.{func.__name__}"
            log = get_logger(func.__module__)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                log.debug(f"{name} executed in {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                log.error(f"{name} failed after {duration_ms:.2f}ms: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator


def log_async_execution_time(operation_name: str = None):
    """Decorator to log execution time of async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            name = operation_name or f"{func.__module__}.{func.__name__}"
            log = get_logger(func.__module__)
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                log.debug(f"{name} executed in {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                log.error(f"{name} failed after {duration_ms:.2f}ms: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator


class MetricsCollector:
    """Collects and reports system metrics."""
    
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
    
    def increment(self, metric_name: str, value: int = 1, tags: dict = None):
        """Increment a counter metric."""
        key = self._make_key(metric_name, tags)
        self.counters[key] = self.counters.get(key, 0) + value
        logger.debug(f"Metric {metric_name} incremented by {value}")
    
    def set_gauge(self, metric_name: str, value: float, tags: dict = None):
        """Set a gauge metric."""
        key = self._make_key(metric_name, tags)
        self.gauges[key] = value
        logger.debug(f"Metric {metric_name} set to {value}")
    
    def record_histogram(self, metric_name: str, value: float, tags: dict = None):
        """Record a histogram value."""
        key = self._make_key(metric_name, tags)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
        logger.debug(f"Histogram {metric_name} recorded: {value}")
    
    def _make_key(self, metric_name: str, tags: dict = None) -> str:
        """Create a key for a metric with tags."""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{metric_name}[{tag_str}]"
        return metric_name
    
    def get_metrics(self) -> dict:
        """Get all collected metrics."""
        return {
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "histograms": {k: len(v) for k, v in self.histograms.items()},
        }


# Global metrics collector
metrics = MetricsCollector()

