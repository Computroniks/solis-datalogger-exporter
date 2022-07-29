# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
import urllib3
from bs4 import BeautifulSoup
import re


class Collector(object) :
    def __init__(self, target: str, uname: str, pwd: str) -> None:
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
        """

        self._target = target
        self._uname = uname
        self._pwd = pwd

        self._http = urllib3.PoolManager()

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

        req = self._http.request("GET", f"http://{self._uname}:{self._pwd}@{self._target}/status.html")
        data = BeautifulSoup(req.data, "html.parser")
        data = data.find_all("script", type="text/javascript")[1].string

        current_pwr: float = float(re.compile("var webdata_now_p = (.*?);").findall(str(data))[0][1:-1])
        yield_today: float = float(re.compile("var webdata_today_e = (.*?);").findall(str(data))[0][1:-1])
        yield_total: float = float(re.compile("var webdata_total_e = (.*?);").findall(str(data))[0][1:-1])

        yield GaugeMetricFamily("solar_current_power", "Current power generation from panels", value=current_pwr)
        yield GaugeMetricFamily("solar_yield_today", "Power generated today", value=yield_today)
        yield CounterMetricFamily("solar_yield_total", "Total power generated all time", value=yield_total)
