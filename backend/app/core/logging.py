import logging
import sys
from typing import Any

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

def setup_logging() -> logging.Logger:
    """
    Setup structured logging for the application.
    
    Returns a configured logger instance.
    """
    # Create logger
    logger = logging.getLogger("scrapy")
    logger.setLevel(LOG_LEVEL)
    
    # Prevent duplicate logging
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logging()

def log_job_created(job_id: str, url: str, mode: str, user_id: str) -> None:
    """Log job creation event."""
    logger.info(f"Job created: {job_id} | URL: {url} | Mode: {mode} | User: {user_id}")

def log_job_completed(job_id: str, duration: float = None) -> None:
    """Log job completion event."""
    msg = f"Job completed: {job_id}"
    if duration:
        msg += f" | Duration: {duration:.2f}s"
    logger.info(msg)

def log_job_failed(job_id: str, error: str) -> None:
    """Log job failure event."""
    logger.error(f"Job failed: {job_id} | Error: {error}")

def log_api_key_created(key_id: str, user_id: str, name: str) -> None:
    """Log API key creation."""
    logger.info(f"API Key created: {key_id} | User: {user_id} | Name: {name}")

def log_api_key_revoked(key_id: str, user_id: str) -> None:
    """Log API key revocation."""
    logger.info(f"API Key revoked: {key_id} | User: {user_id}")

def log_webhook_created(webhook_id: str, url: str, user_id: str) -> None:
    """Log webhook creation."""
    logger.info(f"Webhook created: {webhook_id} | URL: {url} | User: {user_id}")

def log_webhook_dispatched(job_id: str, webhook_url: str, success: bool) -> None:
    """Log webhook dispatch attempt."""
    status = "success" if success else "failed"
    logger.info(f"Webhook dispatched: Job {job_id} | URL: {webhook_url} | Status: {status}")

def log_rate_limit_exceeded(identifier: str) -> None:
    """Log rate limit exceeded event."""
    logger.warning(f"Rate limit exceeded: {identifier}")

def log_ssrf_attempt(url: str, user_id: str) -> None:
    """Log potential SSRF attempt."""
    logger.warning(f"SSRF attempt blocked: {url} | User: {user_id}")
