import logging
import structlog

def custom_renderer(logger, name, event_dict):
    timestamp = event_dict.get("timestamp", "")
    level = event_dict.get("level", "info")
    event = event_dict.get("event", "")
    
    parts = [f"{timestamp} [{level}] {event}"]
    
    # Order: method, path, status_code, duration_ms, request_id
    order = ["method", "path", "status_code", "duration_ms", "request_id"]
    for key in order:
        if key in event_dict:
            parts.append(f"{key}={event_dict[key]}")
            
    # Add any other keys that are not standard
    for key, value in event_dict.items():
        if key not in order and key not in ["timestamp", "level", "event"]:
            parts.append(f"{key}={value}")
            
    return " ".join(parts)

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%SZ", utc=True),
            custom_renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )