import sys
import logging
from loguru import logger
from config import config

# Configure loguru logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level=config.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/geopolitical_sim.log",
    rotation="10 MB",
    retention="1 week",
    level=config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Create a class to intercept standard library logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Configure standard library logging to use loguru
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Export logger
def get_logger(name):
    return logger.bind(name=name)