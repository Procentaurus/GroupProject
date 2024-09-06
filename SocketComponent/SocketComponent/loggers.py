import logging
import os


class DynamicFileHandler(logging.FileHandler):
    def __init__(self, filename, log_dir, *args, **kwargs):
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        super().__init__(os.path.join(log_dir, filename), *args, **kwargs)


def get_game_logger(game_log_id):
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(parent_dir, 'logs', 'game_logs')
    logger = logging.getLogger(f'game_{game_log_id}')

    def setup_timestamp_format(handler):
        formatter = logging.Formatter(
            fmt='{asctime}.{msecs:03.0f} {levelname} [{funcName}] {message}',
            style='{',
            datefmt = '%H:%M:%S'
        )
        handler.setFormatter(formatter)

    if not logger.handlers:
        handler = DynamicFileHandler(f'game_{game_log_id}.log', log_dir)
        setup_timestamp_format(handler)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

def get_server_logger():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(parent_dir, 'logs')
    logger = logging.getLogger(f'server')

    def setup_timestamp_format(handler):
        formatter = logging.Formatter(
            fmt='{asctime}.{msecs:03.0f} {levelname} {message}',
            style='{',
            datefmt = '%H:%M:%S'
        )
        handler.setFormatter(formatter)

    if not logger.handlers:
        handler = DynamicFileHandler('server.log', log_dir)
        setup_timestamp_format(handler)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
