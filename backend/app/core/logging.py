import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(os.path.join(log_dir, "app.log"), maxBytes=10*1024*1024, backupCount=5)
        ]
    )
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("ai_workforce").setLevel(logging.DEBUG)
