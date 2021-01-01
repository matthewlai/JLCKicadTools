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

import os
import re
import sys
import argparse
import errno

from jlc_kicad_tools.logger import Log
from jlc_kicad_tools.jlc_lib.cpl_fix_rotations import ReadDB, FixRotations
from jlc_kicad_tools.jlc_lib.generate_bom import GenerateBOM

DEFAULT_DB_PATH="cpl_rotations_db.csv"

_LOGGER = Log()

def GetOpts():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='Generates BOM and CPL in CSV fashion to be used in JLCPCB Assembly Service', prog='jlc-kicad-tools')
	parser.add_argument('project_dir', metavar='INPUT_DIRECTORY', type=os.path.abspath, help='Directory of KiCad project. If the KiCad project name doesn\t match the directory name, make use of the PROJECT_NAME argument.')
	parser.add_argument('-n', '--project_name', metavar='PROJECT_NAME', type=str, help='The name of the KiCad project in case it doesn\'t match the directory name.', default=None)
	parser.add_argument('-d', '--database', metavar='DATABASE', type=str, help='Filename of database (may be specified more than once)', default=[os.path.join(os.path.dirname(__file__), DEFAULT_DB_PATH)], action='append')
	verbosity = parser.add_argument_group('verbosity arguments')
	verbosity.add_argument('-v', '--verbose', help='Increases log verbosity for each occurrence', dest='verbose_count', action="count", default=0)
	verbosity.add_argument('--warn-no-lcsc-partnumber', help='Enable warning output if lcsc part number is not found', dest='warn_no_partnumber', action='store_true')
	parser.add_argument('--assume-same-lcsc-partnumber', help='Assume same lcsc partnumber for all components of a group', action='store_true', dest='assume_same_lcsc_partnumber')
	parser.add_argument('--include-all-component-groups', help='Include component groups without LCSC part numbers in the BOM', action='store_true', dest='include_all_groups')
	parser.add_argument('-o', '--output', metavar='OUTPUT_DIRECTORY', dest='output_dir', type=os.path.abspath, help='Output directory. Default: INPUT_DIRECTORY')

	if (len(sys.argv) == 1):
		parser.print_help()
		sys.exit()

	return parser.parse_args(sys.argv[1:])

def main():

	opts = GetOpts()

	_LOGGER.SetLevel(opts.verbose_count)

	if not os.path.isdir(opts.project_dir):
		_LOGGER.logger.error("Failed to open project directory: {}".format(opts.project_dir))
		return errno.ENOENT

	# Set default output directory
	if opts.output_dir == None:
		opts.output_dir = opts.project_dir

	if not os.path.isdir(opts.output_dir):
		_LOGGER.logger.info("Creating output directory {}".format(opts.output_dir))
		os.mkdir(opts.output_dir)

	if opts.project_name:
		project_name = opts.project_name
	else:
		project_name = os.path.basename(opts.project_dir)
	_LOGGER.logger.debug("Project name is '%s'.", project_name)

	netlist_filename = project_name + ".xml"
	cpl_filename = project_name + "-all-pos.csv"
	netlist_path = None
	cpl_path = None

	for dir_name, subdir_list, file_list in os.walk(opts.project_dir):
		for file_name in file_list:
			if file_name == netlist_filename and not netlist_path:
				netlist_path = os.path.join(dir_name, file_name)
			elif file_name == cpl_filename and not cpl_path:
				cpl_path = os.path.join(dir_name, file_name)
		if netlist_path and cpl_path:
			break

	if netlist_path is None:
		_LOGGER.logger.error((
		    "Failed to find netlist file: {} in {} (and sub-directories). "
		    "Is the input directory a KiCad project? "
		    "If so, run 'Tools -> Generate Bill of Materials' in Eeschema (any format). "
		    "It will generate an intermediate file we need. "
		    "Note that this is not the same as a netlist for Pcbnew.").format(netlist_filename, opts.project_dir))
		return errno.ENOENT

	if cpl_path is None:
		_LOGGER.logger.error((
			"Failed to find CPL file: {} in {} (and sub-directories). "
			"Run 'File -> Fabrication Outputs -> Footprint Position (.pos) File' in Pcbnew. "
			"Settings: 'CSV', 'mm', 'single file for board'.").format(cpl_filename, opts.project_dir))
		return errno.ENOENT

	_LOGGER.logger.info("Netlist file found at: {}".format(netlist_path))
	_LOGGER.logger.info("CPL file found at: {}".format(cpl_path))

	bom_output_path = os.path.join(opts.output_dir, project_name + "_bom_jlc.csv")
	cpl_output_path = os.path.join(opts.output_dir, project_name + "_cpl_jlc.csv")

	db = {}
	for filename in opts.database:
		db.update(ReadDB(filename))
	if GenerateBOM(netlist_path, bom_output_path, opts) and FixRotations(cpl_path, cpl_output_path, db):
		_LOGGER.logger.info("JLC BOM file written to: {}".format(bom_output_path))
		_LOGGER.logger.info("JLC CPL file written to: {}".format(cpl_output_path))
	else:
		return errno.EINVAL
	return 0

if __name__ == '__main__':
	sys.exit(main())
