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

from jlc_lib import kicad_netlist_reader
import csv
import re

LCSC_PART_NUMBER_MATCHER=re.compile('^C[0-9]+$')

def GenerateBOM(input_filename, output_filename):
  net = kicad_netlist_reader.netlist(input_filename)

  try:
    f = open(output_filename, 'w')
  except IOError:
    print("Failed to open file for writing: {}".format(output_filename))
    return False

  out = csv.writer(f, lineterminator='\n', delimiter=',', quotechar='\"',
                   quoting=csv.QUOTE_ALL)

  out.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])

  grouped = net.groupComponents()

  num_groups_found = 0
  for group in grouped:
    refs = []
    for component in group:
        refs.append(component.getRef())
        c = component

    # Get the field name for the LCSC part number.
    lcsc_part_number = ""
    for field_name in c.getFieldNames():
      field_value = c.getField(field_name)
      if LCSC_PART_NUMBER_MATCHER.match(field_value):
        lcsc_part_number = field_value

    # Skip groups without LCSC part number.
    if lcsc_part_number == "":
      continue

    # They don't seem to like ':' in footprint names.
    footprint = c.getFootprint()
    if footprint.find(':') != -1:
        footprint = footprint[(footprint.find(':') + 1):]

    # Fill in the component groups common data
    out.writerow([c.getValue(), ",".join(refs), footprint, lcsc_part_number])
    num_groups_found += 1

  print("{} component groups found from BOM file.".format(num_groups_found))

  return True