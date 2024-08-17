import logging
import os

class DynamicFileHandler(logging.FileHandler):
    def __init__(self, log_dir, *args, **kwargs):
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        super().__init__(*args, **kwargs)

    def set_filename(self, filename):
        filename = os.path.join(self.log_dir, filename)
        self.baseFilename = os.path.abspath(filename)
        self.stream = self._open()


def get_game_logger(game_log_id):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(parent_dir, 'logs', 'game_logs')
    logger = logging.getLogger(f'game_{game_log_id}')

    def setup_timestamp_format(handler):
        formatter = logging.Formatter(
            fmt='{asctime} {levelname} [{funcName}] {message}',
            style='{',
            datefmt = '%H:%M:%S.%f'[:-3]
        )
        handler.setFormatter(formatter)

    if not logger.handlers:
        handler = DynamicFileHandler(log_dir)
        handler.set_filename(f'game_{game_log_id}.log')
        setup_timestamp_format(handler)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

def get_server_logger():
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(parent_dir, 'logs')
    logger = logging.getLogger(f'server')

    def setup_timestamp_format(handler):
        formatter = logging.Formatter(
            fmt='{asctime} {levelname} {message}',
            style='{',
            datefmt = '%H:%M:%S.%f'[:-3]
        )
        handler.setFormatter(formatter)

    if not logger.handlers:
        handler = DynamicFileHandler(log_dir)
        handler.set_filename(f'server.log')
        setup_timestamp_format(handler)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
