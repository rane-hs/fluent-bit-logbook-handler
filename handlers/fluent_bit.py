from typing import Any, Callable, Optional

from fluent import sender
from logbook import LogRecord, StreamHandler


class FluentHandler(StreamHandler):
    """
    Logging Handler for fluent.
    """

    def __init__(
        self,
        tag: str,
        level: int,
        formatter: Callable[[LogRecord], dict],
        host: str = 'localhost',
        port: int = 24224,
        timeout: float = 3.0,
        verbose: bool = False,
        buffer_overflow_handler: Any = None,
        msgpack_kwargs: Optional[str] = None,
        nanosecond_precision: Any = False,
        **kwargs: str,
    ) -> None:

        self.tag = tag
        self._formatter = formatter
        self._host = host
        self._port = port
        self._timeout = timeout
        self._verbose = verbose
        self._buffer_overflow_handler = buffer_overflow_handler
        self._msgpack_kwargs = msgpack_kwargs
        self._nanosecond_precision = nanosecond_precision
        self._kwargs = kwargs
        self._sender = None
        super().__init__(stream=None, level=level)

    def getSenderClass(self) -> Any:
        return sender.FluentSender

    @property
    def sender(self):  # type: ignore
        if self._sender is None:
            self._sender = self.getSenderInstance(
                tag=self.tag,
                host=self._host,
                port=self._port,
                timeout=self._timeout,
                verbose=self._verbose,
                buffer_overflow_handler=self._buffer_overflow_handler,
                msgpack_kwargs=self._msgpack_kwargs,
                nanosecond_precision=self._nanosecond_precision,
                **self._kwargs,
            )
        return self._sender

    def getSenderInstance(  # type: ignore
        self, tag, host, port, timeout, verbose, buffer_overflow_handler, msgpack_kwargs, nanosecond_precision, **kwargs
    ):
        sender_class = self.getSenderClass()
        return sender_class(
            tag,
            host=host,
            port=port,
            timeout=timeout,
            verbose=verbose,
            buffer_overflow_handler=buffer_overflow_handler,
            msgpack_kwargs=msgpack_kwargs,
            nanosecond_precision=nanosecond_precision,
            **kwargs,
        )

    def emit(self, record):  # type: ignore
        data = self._formatter(record)
        _sender = self.sender
        created = record.time.timestamp()
        return _sender.emit_with_time(
            None, sender.EventTime(created) if _sender.nanosecond_precision else int(created), data
        )

    def close(self) -> None:
        self.acquire()
        try:
            try:
                self.sender.close()
            finally:
                super(FluentHandler, self).close()
        finally:
            self.release()

    def __enter__(self) -> 'FluentHandler':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        self.close()
