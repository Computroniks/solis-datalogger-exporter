#!/usr/env/python3

# SPDX-FileCopyrightText: 2022 Sidings Media <contact@sidingsmedia.com>
# SPDX-License-Identifier: MIT

"""
Call this file to start the application
"""

assert len( __package__ ) > 0, """
The '__main__' module does not seem to have been run in the context of a
runnable package ... did you forget to add the '-m' flag?
Usage: python3 -m datalogger
"""

import sys

from .Exporter import Exporter

def main() -> int:
    """
    main Entry point
    Entrypoint to the application
    :return: Status code 0 = success, any other code indicates faliure
    :rtype: int
    """

    app = Exporter()
    return(app.run())

if __name__ == "__main__":
    sys.exit(main())
    