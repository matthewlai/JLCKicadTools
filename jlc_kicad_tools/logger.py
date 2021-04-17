#!/usr/bin/env python3
# Copyright (C) 2019-2020 Matthew Lai
# Copyright (C) 2019-2020 Kiara Navarro
#
# This file is part of JLC Kicad Tools.
#
# JLC Kicad Tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# JLC Kicad Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JLC Kicad Tools.  If not, see <https://www.gnu.org/licenses/>.

import logging
import logzero


class Log:
    def __init__(self):
        log_format = "%(color)s[%(levelname)s]%(end_color)s %(message)s"
        formatter = logzero.LogFormatter(fmt=log_format)
        logzero.setup_default_logger(formatter=formatter)
        self.logger = logzero.logger

    def SetLevel(self, level):
        # Default log level is WARNING
        logzero.loglevel(max(logging.WARNING - level * 10, logging.NOTSET))
        self.logger.debug(
            "Log level to %s", max(logging.WARNING - level * 10, logging.NOTSET)
        )
