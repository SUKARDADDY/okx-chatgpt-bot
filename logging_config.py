import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory next to this file
log_dir = Path(__file__).resolve().parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "bot.log"

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d \u2013 %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)
