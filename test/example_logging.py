from utils import logger, setup_file_logging

# Basic console logging (already configured)
logger.info("Application started")
logger.debug("This won't show by default (level is INFO)")
logger.warning("This is a warning")
logger.error("This is an error")

# Add file logging with rotation and retention
setup_file_logging(
    log_file="logs/app.log",
    rotation="10 MB",  # New file when reaches 10MB
    retention="30 days",  # Delete logs older than 30 days
    level="DEBUG",  # File will capture DEBUG and above
)

# Now logs go to both console and file
logger.debug("This goes to file only (console is INFO level)")
logger.info("This goes to both console and file")


# Loguru's powerful features
@logger.catch  # Decorator to catch exceptions
def risky_function():
    return 1 / 0


# Better exception handling
try:
    risky_function()
except Exception:  # Fixed: using specific exception instead of bare except
    logger.exception("Something went wrong!")

# Structured logging
logger.info("User logged in", user_id=123, ip="192.168.1.1")

# Context binding
contextualized = logger.bind(request_id="abc123")
contextualized.info("Processing request")
contextualized.info("Request completed")
