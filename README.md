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

### FAQ
1. Why are some components in the generated files but don't show up on JLCPCB preview?

    * Make sure there are no non-ASCII characters in any of the fields. See: https://github.com/matthewlai/JLCKicadTools/issues/45
