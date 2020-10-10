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
import errno

from jlc_kicad_tools.logger import Log
from jlc_kicad_tools.jlc_lib.cpl_fix_rotations import ReadDB, FixRotations
from jlc_kicad_tools.jlc_lib.generate_bom import GenerateBOM

DEFAULT_DB_PATH="cpl_rotations_db.csv"

_LOGGER = Log()

class Component():
	def __init__(self,filename):
		self.file_name = filename
		self.path_name = None
		self.error_message = ""

	def setPath(self,path):
		self.path_name = path

	def setErrorMessage(self,message):
		self.error_message = message

	def isPathFound(self, project_dir):
		if self.path_name is None:
			_LOGGER.logger.error((self.error_message).format(self.file_name, project_dir))
			return errno.ENOENT

def generateFilePath(dir_name, file_name):
	return os.path.join(dir_name, file_name)

def getOpts():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='Generates BOM and CPL in CSV fashion to be used in JLCPCB Assembly Service', prog='jlc-kicad-tools')
	parser.add_argument('project_dir', metavar='INPUT_DIRECTORY', type=os.path.abspath, help='Directory of KiCad project. Name should match KiCad project name.')
	parser.add_argument('-d', '--database', metavar='DATABASE', type=str, help='Filename of database', default=os.path.join(os.path.dirname(__file__), DEFAULT_DB_PATH))
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

	opts = getOpts()

	_LOGGER.setLevel(opts.verbose_count)

	if not os.path.isdir(opts.project_dir):
		_LOGGER.logger.error("Failed to open project directory: {}".format(opts.project_dir))
		return errno.ENOENT

	# Set default output directory
	if opts.output_dir == None:
		opts.output_dir = opts.project_dir

	if not os.path.isdir(opts.output_dir):
		_LOGGER.logger.info("Creating output directory {}".format(opts.output_dir))
		os.mkdir(opts.output_dir)

	project_name = os.path.basename(opts.project_dir)
	_LOGGER.logger.debug("Project name is '%s'.", project_name)

	netlist = Component(project_name + ".xml")
	cpl = Component(project_name + "-all-pos.csv")
	cpl.setErrorMessage("Failed to find CPL file: {} in {} (and sub-directories). "
	"Run 'File -> Fabrication Outputs -> Footprint Position (.pos) File' in Pcbnew. "
	"Settings: 'CSV', 'mm', 'single file for board'.")
	netlist.setErrorMessage("Failed to find netlist file: {} in {} (and sub-directories). "
	"Is the input directory a KiCad project? "
	"If so, run 'Tools -> Generate Bill of Materials' in Eeschema (any format). "
	"It will generate an intermediate file we need. "
	"Note that this is not the same as a netlist for Pcbnew.")

	for dir_name, subdir_list, file_list in os.walk(opts.project_dir):
		for file_name in file_list:
			if file_name == netlist.file_name:
				netlist.setPath(os.path.join(dir_name, file_name))
			elif file_name == cpl.file_name:
				cpl.setPath(os.path.join(dir_name, file_name))

	netlist.isPathFound(opts.output_dir)
	cpl.isPathFound(opts.output_dir)

	_LOGGER.logger.info("Netlist file found at: {}".format(netlist.path_name))
	_LOGGER.logger.info("CPL file found at: {}".format(cpl.path_name))

	bom_output_path = generateFilePath(opts.output_dir, project_name + "_bom_jlc.csv")
	cpl_output_path = generateFilePath(opts.output_dir, project_name + "_cpl_jlc.csv")

	db = ReadDB(opts.database)
	if GenerateBOM(netlist.path_name, bom_output_path, opts) and FixRotations(cpl.path_name, cpl_output_path, db):
		_LOGGER.logger.info("JLC BOM file written to: {}".format(bom_output_path))
		_LOGGER.logger.info("JLC CPL file written to: {}".format(cpl_output_path))
	else:
		return errno.EINVAL
	return 0

if __name__ == '__main__':
	sys.exit(main())
