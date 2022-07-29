# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

from dotenv import load_dotenv
import os
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server

from .Collector import Collector
from .Logging import log
from .Errors import FatalError


class Exporter:
    def __init__(self) -> None:
        """
        __init__ Create instance of exporter

        Main control class for the datalogger exporter. This class
        starts the server and controls all aspects of the application.

        :raises FatalError: An unrecoverable error
        """

        load_dotenv()

        self._target = os.getenv("DATALOGGER_IP")
        self._uname = os.getenv("DATALOGGER_IP")
        self._pwd = os.getenv("DATALOGGER_PWD")

        try:
            self._retries = int(os.getenv("DATALOGGER_RETRIES"))
        except ValueError:
            log.error("ENVIRONMENT", "Invalid value for DATALOGGER_RETRIES. Expected integer")
            raise FatalError

        try:
            self._port = int(os.getenv("EXPORTER_PORT"))
        except ValueError:
            log.error("ENVIRONMENT", "Invalid value for EXPORTER_PORT. Expected integer")
            raise FatalError

        REGISTRY.register(Collector(self._target, self._uname, self._pwd))

    def run(self) -> int:
        """
        run Run the application
        Main loop of the application.
        :return: Status code
        :rtype: int
        """

        # Wrap all actions in try except in order to handle all Fatal
        # exceptions and keyboard interupts. In order to pass a fatal
        # interupt down through from other errors, the FatalError should
        # be raised.
        try:
            self._startServer()

            # Main application loop
            while True:
                pass
        
        except FatalError:
            return self._halt(1)

        except KeyboardInterrupt:
            log.info("APPLICATION", "Keyboard interupt detected, shutting down")
            return self._halt()

    def _startServer(self) -> None:
        """
        _startServer Start the prometheus web server
        """

        log.info("WEB SERVER", f"Starting the Prometheus metrics server on port {self._port}")

        try:
            start_http_server(port=self._port)
        except Exception as e:
            log.error("WEB SERVER", f"Unhandled exception: {e}")
            raise FatalError(e)
        else:
            log.info("WEB SERVER", "Successfully started server")

    def _halt(self, status: int = 0) -> int:
        """
        _halt End the program
        Exit the program after cleaning up
        :param status: Exit code. 0 = success. Any other value means
            error, defaults to 0
        :type status: int, optional
        :return: Status code
        :rtype: int
        """

        log.info("APPLICATION", "Final shutdown message")
        return status