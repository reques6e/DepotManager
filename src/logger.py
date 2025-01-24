import logging
from datetime import datetime

from pythonjsonlogger import jsonlogger

_logger = logging.getLogger()

logHandler = logging.StreamHandler()

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


formatter = CustomJsonFormatter(
    '%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s'
)
# fileHandler = logging.FileHandler('{0}/{1}.log'.format(logPath, fileName))

logHandler.setFormatter(formatter)
_logger.addHandler(logHandler)
# _logger.addHandler(fileHandler)
_logger.setLevel(logging.INFO)