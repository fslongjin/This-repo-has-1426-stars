"""
The MIT License (MIT)

Copyright (c) 2022-present a3510377( 猴貓 )

Rich Logging
"""

import re
import copy
from pathlib import Path
from datetime import timedelta, datetime
import logging
from logging import LogRecord, Logger, Formatter
from logging.handlers import BaseRotatingHandler
from typing import Optional, Union

import rich
from rich.text import Text
from rich.theme import Style, Theme
from rich.logging import RichHandler
from rich.syntax import PygmentsSyntaxTheme
from pygments.styles.monokai import MonokaiStyle


log = logging.getLogger("logging")
StrPath = Union[Path, str]


class LogTimeRotatingFileHandler(BaseRotatingHandler):
    """
    from logging mode Modify
    """

    def __init__(
        self,
        filename: str,
        directory: Optional[StrPath] = None,
        markup: bool = False,
        expired_interval: timedelta = timedelta(days=8),
        maxBytes: int = 1e6,
        backupCount: int = 5,
        encoding: str = "utf-8",
    ) -> None:
        directory = Path(directory or Path("logs"))
        directory.mkdir(parents=True, exist_ok=True)

        filepath = directory / f"{filename}.log"

        super().__init__(
            filepath,
            mode="a",
            encoding=encoding,
            delay=False,
        )

        self.filename = filename
        self.directory = directory
        self.markup = markup
        self.interval_time = timedelta(days=1)
        self.expired_interval = expired_interval
        self.maxBytes = maxBytes
        self.backupCount = backupCount

        self.rolloverAt = self.computeRollover()

    def computeRollover(self) -> datetime:
        return datetime.today() - self.interval_time

    def format(self, record: LogRecord):
        if self.markup:
            try:
                record = copy.deepcopy(record)
                record.msg = Text.from_markup(record.msg)
            except Exception as e:  # fix: aiohttp throw errors
                log.debug(e)

        return (self.formatter or Formatter()).format(record)

    def shouldRollover(self, record: LogRecord) -> bool:
        if self.stream is None:
            self.stream = self._open()
        if self.rolloverAt >= datetime.today():
            return True

        if self.maxBytes > 0:
            self.stream.seek(0, 2)
            if self.stream.tell() + len(f"{record.msg}\n") >= self.maxBytes:
                return True

        return False

    def delete_expired_logs(self) -> None:
        file_time_re = re.compile(
            rf"{self.filename}\-"
            r"(?P<time>\d{4}\-\d{2}\-\d{2})"
            r"(\.(?P<part>\d))?\.log"
        )
        end_time = datetime.today() - self.expired_interval

        for file in self.directory.iterdir():
            if (match := file_time_re.match(file.name)) and datetime.strptime(
                match.groupdict()["time"], "%Y-%m-%d"
            ) < end_time:
                log.info(f"Deleting old log file: {file.name}")
                file.unlink(missing_ok=True)

    def get_file_name(
        self,
        filename: Optional[Union[str, object]] = None,
        *,
        base_file: bool = True,
        time: bool = True,
        time_str: Optional[str] = None,
    ) -> Path:
        filenames = []

        if base_file:
            filenames.append(str(self.filename))
        if time and time_str is not None:
            filenames.append(
                datetime.now().strftime("%Y-%m-%d") if time_str is None else time_str
            )
        if filename:
            filenames.append(str(filename))

        return self.directory / f"{'.'.join(filenames)}.log"

    def doRollover(self) -> bool:
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.rolloverAt >= datetime.today():
            for i in range(self.backupCount, 0, -1):
                if (old_file := self.get_file_name(i, time=False)).exists():
                    old_file.rename(
                        self.get_file_name(
                            i, time_str=self.rolloverAt.strftime("%Y-%m-%d")
                        )
                    )
            self.rolloverAt = self.computeRollover()
            return self.delete_expired_logs()

        if self.backupCount > 0:
            self.get_file_name(self.backupCount, time=False).unlink(missing_ok=True)
            for i in range(self.backupCount - 1, 0, -1):
                if (old_file := self.get_file_name(i, time=False)).exists():
                    old_file.rename(self.get_file_name(i + 1, time=False))
            (base_file := self.get_file_name(time=False)).rename(
                base_file.with_suffix(".1.log")
            )

        self.stream = self._open()


def init_logging(level: int, directory: Optional[StrPath] = None) -> Logger:
    warnings_logger = logging.getLogger("py.warnings")

    log.setLevel(level)
    warnings_logger.setLevel(logging.WARNING)

    shell_formatter = logging.Formatter("{message}", datefmt="[%X]", style="{")
    file_formatter = logging.Formatter(
        "[{asctime}] [{levelname}:{name}]: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    rich_console = rich.get_console()
    rich_console.push_theme(
        Theme(
            {
                "log.time": Style(dim=True),
                "logging.level.warning": Style(color="yellow"),
                "logging.level.critical": Style(color="white", bgcolor="red"),
                "logging.level.verbose": Style(color="magenta", italic=True, dim=True),
                "logging.level.trace": Style(color="white", italic=True, dim=True),
                "repr.number": Style(color="cyan"),
                "repr.url": Style(
                    underline=True,
                    italic=True,
                    bold=False,
                    color="cyan",
                ),
            }
        )
    )
    shell_handler = RichHandler(
        markup=True,
        console=rich_console,
        tracebacks_theme=(PygmentsSyntaxTheme(MonokaiStyle)),
    )
    shell_handler.setLevel(logging.DEBUG)
    shell_handler.setFormatter(shell_formatter)

    file_handler = LogTimeRotatingFileHandler(
        log.name, markup=True, directory=directory
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(shell_handler)

    return log
