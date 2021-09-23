from setuptools import setup, find_packages
from jlc_kicad_tools import __version__

setup(
    name='jlc-kicad-tools',
    version=__version__,
    description='JLCKicadTools is a tool aims to work with JLCPCB assembly service featuring KiCad 5',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/matthewlai/JLCKicadTools',
    author='Matthew Lai',
    license='GPL3',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires = ['logzero>=1.5'],
    entry_points={"console_scripts": [
                    "jlc-kicad-tools = jlc_kicad_tools.generate_jlc_files:main"
                ]
    },
)
