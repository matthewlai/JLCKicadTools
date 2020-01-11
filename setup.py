from setuptools import setup, find_packages
from kicad_jlc_tool import __version__

setup(
    name='kicad-jlc-tool',
    version=__version__,
    description='JLCKicadTools is a tool aims to work with JLCPCB assembly service featuring KiCad 5',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/matthewlai/JLCKicadTools',
    author='Matthew Lai',
    license='GPL3',
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["kicad-jlc-tool=kicad_jlc_tool.generate_jlc_files:main"]},
)
