# GRIB Tools

This repository is a collection of tools in Python for working with GRIB using
[ecCodes](https://software.ecmwf.int/wiki/display/ECC/ecCodes+Home) by ECMWF.

The package is intended to make it easier to perform common tasks with GRIB
files that typically are easier to do in a script or program than using the
command line tools provided by ecCodes and GRIB API. It intentionally uses
the low-level Python API provided natively by these libraries in order to
avoid unnecessary dependencies.

It is not intended to ease work with GRIBs in general by providing a
higher-level API. Other packages provide such functions (see e.g.
[PythonicGrib](https://github.com/erget/PythonicGRIB)), but they are not
utilized here for maximal portability.

## Compatibility with GRIB API

Symbols are imported from ``eccodes`` inside ``try`` statements. If an
``ImportError`` is raised, the same symbols are imported from ``gribapi``.
Because only names, and not their call signatures, were changed when writing
ecCodes, this effectively masks the names so that the rest of the scripts can
run without problems.
