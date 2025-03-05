import logging
import google.cloud.logging

def setup_cloud_logging():

    client = google.cloud.logging.Client()
    client.setup_logging()

def get_logger(name):

    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    return logger

setup_cloud_logging()
