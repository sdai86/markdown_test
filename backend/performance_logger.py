import time
import logging
import json
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceLogger:
    """Utility class for logging performance metrics."""
    
    def __init__(self):
        self.metrics = []
        
    @contextmanager
    def measure(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager to measure operation duration."""
        start_time = time.time()
        start_perf = time.perf_counter()
        
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_perf) * 1000
            
            metric = {
                'operation': operation,
                'duration_ms': duration_ms,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
            self.metrics.append(metric)
            
            # Log the metric
            logger.info(f"PERF: {operation} took {duration_ms:.2f}ms", extra=metric)
            
    def log_metric(self, operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Manually log a performance metric."""
        metric = {
            'operation': operation,
            'duration_ms': duration_ms,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        self.metrics.append(metric)
        logger.info(f"PERF: {operation} took {duration_ms:.2f}ms", extra=metric)
        
    def get_metrics(self) -> list:
        """Get all collected metrics."""
        return self.metrics.copy()
        
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.metrics:
            return {}
            
        operations = {}
        for metric in self.metrics:
            op = metric['operation']
            if op not in operations:
                operations[op] = []
            operations[op].append(metric['duration_ms'])
            
        summary = {}
        for op, durations in operations.items():
            summary[op] = {
                'count': len(durations),
                'avg_ms': sum(durations) / len(durations),
                'min_ms': min(durations),
                'max_ms': max(durations),
                'total_ms': sum(durations)
            }
            
        return summary
        
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()

# Global performance logger instance
perf_logger = PerformanceLogger()

# Decorator for measuring function performance
def measure_performance(operation_name: Optional[str] = None):
    """Decorator to measure function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            with perf_logger.measure(op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Context manager for measuring code blocks
@contextmanager
def measure_time(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager to measure arbitrary code blocks."""
    with perf_logger.measure(operation, metadata):
        yield

def log_performance_summary():
    """Log a summary of all performance metrics."""
    summary = perf_logger.get_summary()
    if summary:
        logger.info("Performance Summary:")
        for operation, stats in summary.items():
            logger.info(f"  {operation}: {stats['count']} calls, "
                       f"avg: {stats['avg_ms']:.2f}ms, "
                       f"min: {stats['min_ms']:.2f}ms, "
                       f"max: {stats['max_ms']:.2f}ms")
    else:
        logger.info("No performance metrics collected")

# Performance monitoring middleware for FastAPI
class PerformanceMiddleware:
    """Middleware to automatically measure API endpoint performance."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.perf_counter()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    
                    # Extract request info
                    method = scope["method"]
                    path = scope["path"]
                    operation = f"{method} {path}"
                    
                    # Log the performance metric
                    perf_logger.log_metric(
                        operation=operation,
                        duration_ms=duration_ms,
                        metadata={
                            "method": method,
                            "path": path,
                            "status_code": message.get("status", 0)
                        }
                    )
                    
                await send(message)
                
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
