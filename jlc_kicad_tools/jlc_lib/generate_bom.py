# Copyright (C) 2019 Matthew Lai
# Copyright (C) 1992-2019 Kicad Developers Team
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

from jlc_kicad_tools.jlc_lib import kicad_netlist_reader
import csv
import re
from jlc_kicad_tools.logger import Log

_LOGGER = Log()

LCSC_PART_NUMBER_MATCHER = re.compile("^C[0-9]+$")


def GenerateBOM(input_filename, output_filename, opts):
    net = kicad_netlist_reader.netlist(input_filename)

    try:
        f = open(output_filename, mode="w", encoding="utf-8")
    except IOError:
        _LOGGER.logger.error(
            "Failed to open file for writing: {}".format(output_filename)
        )
        return False

    out = csv.writer(
        f, lineterminator="\n", delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
    )

    out.writerow(["Comment", "Designator", "Footprint", "LCSC Part Number"])

    grouped = net.groupComponents()

    num_groups_found = 0
    for group in grouped:
        refs = []
        lcsc_part_number = None
        footprints = set()

        for component in group:
            refs.append(component.getRef().upper())
            c = component
            # All components in a group should have the same part number
            lcsc_part_number = c.getLcscPartNumber()

            if c.getFootprint() != "":
                footprints.add(c.getFootprint())

        if lcsc_part_number is None:
            if opts.warn_no_partnumber:
                _LOGGER.logger.warning(
                    "No LCSC part number found for components {}".format(",".join(refs))
                )
            if not opts.include_all_groups:
                continue
            lcsc_part_number = "no_part_number"

        # Check footprints for uniqueness
        if len(footprints) == 0:
            _LOGGER.logger.error(
                "No footprint found for components {}".format(",".join(refs))
            )
            return False
        if len(footprints) != 1:
            _LOGGER.logger.error(
                "Components {components} from same group have different foot prints: \
                {footprints}".format(
                    components=", ".join(refs), footprints=", ".join(footprints)
                )
            )
            return False
        footprint = list(footprints)[0]

        # They don't seem to like ':' in footprint names.
        footprint = footprint[(footprint.find(":") + 1):]

        # Fill in the component groups common data
        out.writerow([c.getValue(), ",".join(refs), footprint, lcsc_part_number])
        num_groups_found += 1

    _LOGGER.logger.info(
        "{} component groups found from BOM file.".format(num_groups_found)
    )

    return True
