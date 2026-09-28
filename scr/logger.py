import logging 

logging.basicConfig(
    filename="app.log",
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s"

)

def log_message(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def log_warning(message):
    logging.warning(message)