from setuptools import setup, find_packages

import grib_tools

DESCRIPTION = grib_tools.__doc__

setup(
    name='grib_tools',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/erget/grib-tools',
    license='Apache 2.0',
    author='Daniel Lee',
    author_email='Daniel.Lee@dwd.de',
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    install_requires=[
        "numpy"
    ],
    dependency_links=[
        "https://software.ecmwf.int/wiki/display/ECC/ecCodes+Home"
    ],
    entry_points={
        "console_scripts":
        ["validate_encoding = grib_tools.validate_encoding:main"]
    }
)
