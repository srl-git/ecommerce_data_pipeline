import logging
import google.cloud.logging

def setup_cloud_logging():

    client = google.cloud.logging.Client(_use_grpc=False)
    client.setup_logging()

def get_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(format)
        logger.addHandler(console_handler)
    return logger
