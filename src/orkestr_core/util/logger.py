import logging
import traceback

class CustomStreamHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno == logging.ERROR and record.exc_info is not False:
            record.msg = f"{record.msg}\n{traceback.format_exc()}"
        super().emit(record)

def setup_logger(name=None):
    # Create a custom logger
    logger = logging.getLogger(name if name else __name__)
    logger.setLevel(logging.INFO) 

    # Create handlers
    c_handler = CustomStreamHandler()
    c_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)

    return logger