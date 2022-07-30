# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
import urllib3
from urllib3.exceptions import MaxRetryError
from bs4 import BeautifulSoup
import re

from .Logging import log


class Collector(object) :
    def __init__(self, target: str, uname: str, pwd: str, retries: int, timeout: int) -> None:
        """
        __init__ Create instance of datalogger collector

        Prometheus collector for the Solis solar inverter data logging
        stick.

        :param target: IP of datalogging stick
        :type target: str
        :param uname: Username to use to login to web interface
        :type uname: str
        :param pwd: Password to use to login to web interface
        :type pwd: str
        :param retries: Number of retries to attempt
        :type retries: int
        :param timeout: Timeout for connections
        :type timeout: int
        """

        self._target = target
        self._uname = uname
        self._pwd = pwd

        self._http = urllib3.PoolManager(retries=urllib3.Retry(retries), timeout=urllib3.Timeout(timeout))

        self._current_pwr: float = 0
        self._yield_today: float = 0
        self._yield_total: float = 0

    def collect(self):
        """
        collect Collect method for Prometheus exporter

        :yield: Current power generation
        :rtype: GuageMetricFamily
        :yield: Total generation today
        :rtype: GuageMetricFamily
        :yield: Total generation all time
        :rtype: CounterMetricFamily
        """

        try:
            req = self._http.request("GET", f"http://{self._uname}:{self._pwd}@{self._target}/status.html")
        except MaxRetryError:
            # Stick must be offline so no generation. Leave totals same
            # but set generation to 0
            log.info("EXPORTER", "Unable to contact logging stick. Assuming no generation.")
            self._current_pwr = 0
        else:
            if req.status != 200:
                log.error("EXPORTER", "Failed to log into web interface. Check username and password.")
                self._current_pwr = 0
            else:
                data = BeautifulSoup(req.data, "html.parser")
                data = data.find_all("script", type="text/javascript")[1].string

                self._current_pwr = float(re.compile("var webdata_now_p = (.*?);").findall(str(data))[0][1:-1])
                self._yield_today = float(re.compile("var webdata_today_e = (.*?);").findall(str(data))[0][1:-1])
                self._yield_total = float(re.compile("var webdata_total_e = (.*?);").findall(str(data))[0][1:-1])

        yield GaugeMetricFamily("solar_current_power", "Current power generation from panels", value=self._current_pwr)
        yield GaugeMetricFamily("solar_yield_today", "Power generated today", value=self._yield_today)
        yield CounterMetricFamily("solar_yield_total", "Total power generated all time", value=self._yield_total)
