# JLCKicadTools

## Overview

JLCKicadTools is a tool aims to work with JLCPCB assembly service featuring KiCad 5.

See [this blog post](https://dubiouscreations.com/2019/10/21/using-kicad-with-jlcpcb-assembly-service) for instructions.

## Requirements
Python 3.6+

### Installation
```
pip install git+https://github.com/matthewlai/JLCKicadTools
pip install -r requirements.txt
```

In case you do not have pip installed. See:

### Fedora
```
sudo dnf install python-pip
```

### Debian and Ubuntu
```
sudo apt-get install python-pip
```

### How to use
JLCKicadTools comes as a nice command line interface named kicad-jlc-tool.
To see how it works just simply issue at your shell prompt:

```
$ jlc-kicad-tools
```

### KiCad

1. Design your board as usual
1. Create a custom field in Eeschema (for instance LCSCStockCode) and add in the components "C" stock number from JLCPCB/LCSC
1. Once you are satisfied with your board design, go to Eeschema and run “Tools -> Generate Bill of Materials”
1. Go to Pcbnew and run ‘File -> Fabrication Outputs -> Footprint Position (.pos) File’.
1. Plot gerbers as per usual for PCB manufacturing
1. Run the script and give it the project directory

```
generate_jlc_files.py --warn-no-lcsc-partnumber --database=cpl_rotations_db.csv --verbose myprojectfolder
```
1. Upload your Gerber and CPL/BOM files to JLCPCB
1. Review the rotations of components on the website, for any that are rotated incorrectly you can override the angle using the "JLCPCBRotation" custom KiCad field, once added, repeat these steps to generate fresh BOM/CPL files (no need to generate Gerber again unless you moved components)

