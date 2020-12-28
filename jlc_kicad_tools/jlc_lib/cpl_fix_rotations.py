# Copyright (C) 2019 Matthew Lai
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

import csv
import re
import sys
from jlc_kicad_tools.logger import Log
import xml.etree.ElementTree as ET


# JLC requires columns to be named a certain way.
HEADER_REPLACEMENT_TABLE={
  "Ref": "Designator",
  "PosX": "Mid X",
  "PosY": "Mid Y",
  "Rot": "Rotation",
  "Side": "Layer"
}

_LOGGER = Log()

def ReadDB(filename):
  db = {}
  with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      if row[0] == "Footprint pattern":
        continue
      else:
        db[re.compile(row[0])] = int(row[1])
  _LOGGER.logger.info("Read {} rules from {}".format(len(db), filename))
  return db

def ReadNetlistJLCPCBRotation(netlist_filename):
	# Parse the NETLIST looking for custom fields named JLCPCBRotation (case sensitive)
	fixed_rotation_db = {}
	tree = ET.parse(netlist_filename)
	root = tree.getroot()	
	for component in root.findall('components/comp'):
		JLCPCBRotation = component.find('./fields/field[@name="JLCPCBRotation"]')
		if JLCPCBRotation!=None:
			angle =float(JLCPCBRotation.text)
			ref = component.attrib["ref"]
			fixed_rotation_db[ref]=angle
			_LOGGER.logger.info("JLCPCBRotation override applied to {} {:.6f}".format(ref,angle))
	return fixed_rotation_db
  
def FixRotations(input_filename, output_filename, db, fixed_rotation_db):
  with open(input_filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    writer = csv.writer(open(output_filename, 'w', newline=''), delimiter=',')
    package_index = None
    rotation_index = None
    posx_index = None
    side_index = None
    ref_index = None
    for row in reader:
      if not package_index:
        # This is the first row. Find "Package" and "Rot" column indices.
        for i in range(len(row)):
          if row[i] == "Package":
            package_index = i
          elif row[i] == "Ref":
            ref_index = i
          elif row[i] == "Rot":
            rotation_index = i
          elif row[i] == "PosX":
            posx_index = i
          elif row[i] == "Side":
            side_index = i
        if package_index is None:
          _LOGGER.logger.warning("Failed to find 'Package' column in the csv file")
          return False
        if ref_index is None:
          _LOGGER.logger.warning("Failed to find 'Ref' column in the csv file")
          return False
        if rotation_index is None:
          _LOGGER.logger.warning("Failed to find 'Rot' column in the csv file")
          return False
        if side_index is None:
          _LOGGER.logger.warning("Failed to find 'Side' column in the csv file")
          return False
        if posx_index is None:
          _LOGGER.logger.warning("Failed to find 'PosX' column in the csv file")
          return False
        # Replace column names with labels JLC wants.
        for i in range(len(row)):
          if row[i] in HEADER_REPLACEMENT_TABLE:
            row[i] = HEADER_REPLACEMENT_TABLE[row[i]]
      else:
        rotation = float(row[rotation_index])
        if row[side_index].strip() == "bottom":
          row[posx_index] = "{0:.6f}".format(-float(row[posx_index]))
        for pattern, correction in db.items():
          if pattern.match(row[package_index]):
            _LOGGER.logger.info("Footprint {} matched {}. Applying {} deg correction"
                .format(row[package_index], pattern.pattern, correction))
            if row[side_index].strip() == "bottom":
                rotation = (rotation - correction) % 360
            else:
                rotation = (rotation + correction) % 360
            row[rotation_index] = "{0:.6f}".format(rotation)
            break
        for ref, angle in fixed_rotation_db.items():
          if ref==row[ref_index]:
            _LOGGER.logger.info("Reference {},  fixed {} deg correction"
                .format(row[ref_index], angle))
            row[rotation_index] = "{0:.6f}".format(angle)
            break
      writer.writerow(row)
  return True
