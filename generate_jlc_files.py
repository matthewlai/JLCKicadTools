#!/usr/bin/env python3
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

import os
import re
import sys
import argparse
import logging

from jlc_lib.cpl_fix_rotations import ReadDB, FixRotations
from jlc_lib.generate_bom import GenerateBOM

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('project_dir', metavar='project directory', type=os.path.abspath, nargs='?', help='Directory of KiCad project', default=os.getcwd())
	parser.add_argument('-d', '--database', metavar='database', type=str, help='Filename of database', default=os.path.join(os.path.dirname(__file__), "cpl_rotations_db.csv"))
	parser.add_argument('-v', '--verbose', help='increases log verbosity for each occurrence', dest='verbose_count', action="count", default=0)
	parser.add_argument('--warn-no-lcsc-partnumber', help='warn if ', dest='warn_no_partnumber', action='store_true')
	parser.add_argument('--assume-same-lcsc-partnumber', help='assume same lcsc partnumber for all components of a group', action='store_true', dest='assume_same_lcsc_partnumber')

	# Parse arguments
	opts = parser.parse_args(sys.argv[1:])

	logging.basicConfig(format="%(message)s", level=max(3 - opts.verbose_count, 0) * 10)

	if not os.path.isdir(opts.project_dir):
		logging.error("Failed to open project directory: {}".format(opts.project_dir))
		return -1

	project_name = os.path.basename(opts.project_dir)
	logging.debug("Project name is '%s'.", project_name)
	netlist_filename = project_name + ".xml"
	cpl_filename = project_name + "-all-pos.csv"
	netlist_path = None
	cpl_path = None

	for dir_name, subdir_list, file_list in os.walk(opts.project_dir):
		for file_name in file_list:
			if file_name == netlist_filename:
				netlist_path = os.path.join(dir_name, file_name)
			elif file_name == cpl_filename:
				cpl_path = os.path.join(dir_name, file_name)

	if netlist_path is None:
		logging.error((
			"Failed to find netlist file: {} in {} (and sub-directories). "
			"Run 'Tools -> Generate Bill of Materials' in Eeschema (any format). "
			"It will generate an intermediate file we need.").format(netlist_filename, opts.project_dir))
		return -1

	if cpl_path is None:
		logging.error((
			"Failed to find CPL file: {} in {} (and sub-directories). "
			"Run 'File -> Fabrication Outputs -> Footprint Position (.pos) File' in Pcbnew. "
			"Settings: 'CSV', 'mm', 'single file for board'.").format(cpl_filename, opts.project_dir))
		return -1

	logging.info("Netlist file found at: {}".format(netlist_path))
	logging.info("CPL file found at: {}".format(cpl_path))

	bom_output_path = os.path.join(opts.project_dir, project_name + "_bom_jlc.csv")
	cpl_output_path = os.path.join(opts.project_dir, project_name + "_cpl_jlc.csv")

	db = ReadDB(opts.database)
	if GenerateBOM(netlist_path, bom_output_path, opts) and FixRotations(cpl_path, cpl_output_path, db):
		logging.info("JLC BOM file written to: {}".format(bom_output_path))
		logging.info("JLC CPL file written to: {}".format(cpl_output_path))
	else:
		return -1

	return 0

if __name__ == '__main__':
	sys.exit(main())