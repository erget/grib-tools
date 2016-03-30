"""
Test for encoding/decoding CCSDS.
"""

from __future__ import print_function

import argparse
import os
from logging import info
from os import listdir
from os.path import isfile, join

import numpy as np

from eccodes import (codes_clone,
                     codes_get,
                     codes_get_values,
                     codes_grib_new_from_file,
                     codes_release,
                     codes_set,
                     codes_set_values,
                     codes_write)


def repack_grib(input_file, output_file, packing_type):
    """Repack all GRIBs in input_file."""

    # minmaxmean_values = []
    orig_min = orig_max = orig_mean = 0
    packed_min = packed_max = packed_mean = 0

    # print("Repack "+input_file+" to "+output_file)

    with open(input_file) as infile:
        while True:
            in_gid = codes_grib_new_from_file(infile)
            if in_gid is None:
                break
            payload = codes_get_values(in_gid)
            orig_min = np.min(payload)
            orig_max = np.max(payload)
            orig_mean = np.mean(payload)
            clone_id = codes_clone(in_gid)
            codes_set(clone_id, "packingType", packing_type)
            codes_set_values(clone_id, payload)
            with open(output_file, "w") as output:
                codes_write(clone_id, output)
            codes_release(clone_id)
            codes_release(in_gid)

    with open(output_file) as output:
        gid = codes_grib_new_from_file(output)

        encoded_type = codes_get(gid, "packingType")
        if encoded_type != packing_type:
            err_msg = "Repacking failed silently."
            info(err_msg)
            raise RuntimeError(err_msg)

        payload_packed = codes_get_values(gid)
        packed_min = np.min(payload_packed)
        packed_max = np.max(payload_packed)
        packed_mean = np.mean(payload_packed)
        codes_release(gid)

    if (abs(orig_min - packed_min) > 0 or
            abs(orig_max - packed_max) > 0 or
            abs(orig_mean - packed_mean) > 0):
        err_msg = "Repacking yields different min,max or mean!."
        info(err_msg)
    #            raise RuntimeError(err_msg)

    minmaxmean_values = [orig_min, orig_max, orig_mean, packed_min, packed_max,
                         packed_mean]
    return minmaxmean_values


def repack_and_check(input_dir, target_packing_type):
    """Repack all GRIBs in input_dir with target_packing_type."""

    filelist = [join(input_dir, f) for f in listdir(input_dir) if
                f.endswith("." + target_packing_type) or f.endswith(
                    ".reverted")]
    if len(filelist) > 0:
        for f in filelist:
            os.remove(f)

    gribfiles = [join(input_dir, f) for f in listdir(input_dir) if
                 isfile(join(input_dir, f))]

    for input_file in gribfiles:
        infile = open(input_file)
        in_gid = codes_grib_new_from_file(infile)
        infile.close()
        original_encoded_type = codes_get(in_gid, "packingType")
        codes_release(in_gid)

        outfile = input_file + "." + target_packing_type
        outfile2 = input_file + ".reverted"

        print("Repack " + input_file + " to " + target_packing_type +
              " & revert to " + original_encoded_type)

        values_2ccsds = repack_grib(input_file, outfile, target_packing_type)
        values_2orig = repack_grib(outfile, outfile2, original_encoded_type)
        print("values orig -> ccsds       min,max,mean : " + str(values_2ccsds))
        print("values ccsds > orig/simple min,max,mean : " + str(values_2orig))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__[1:-1])
    parser.add_argument("grib", nargs="+", help="GRIB file to process")
    args = parser.parse_args()

    gribfiles = [os.path.realpath(x) for x in args.grib]

    for gribfile in gribfiles:
        info("Working with GRIBS in {}".format(gribfile))
        repack_and_check(gribfile, "grid_ccsds")
