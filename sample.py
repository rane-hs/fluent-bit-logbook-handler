from logbook import INFO, Logger, LogRecord
from handlers.fluent_bit import FluentHandler


def _plain_formatter(record: LogRecord) -> dict:
    return dict(time=f'{record.time:%Y-%m-%d %H:%M:%S.%f%z}', channel=f'{record.channel}', message=f'{record.message}')


if __name__ == '__main__':
    logger = Logger('fluentd-logbook')
    h = FluentHandler(tag='api-app', level=INFO, host='logger-container', formatter=_plain_formatter)
    logger.handlers.append(h)
    logger.info("INFO")
    logger.warn("WARN")
    logger.error("ERROR")
