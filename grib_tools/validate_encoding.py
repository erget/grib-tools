# Copyright 2016 Deutscher Wetterdienst
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test encoding/decoding CCSDS.

This uses a version of ecCodes modified with the following patch:

    From 3825f6c3e9278914a2e74d7d1a6015be457be0d4 Mon Sep 17 00:00:00 2001
    From: Mathis Rosenhauer <rosenhauer@dkrz.de>
    Date: Thu, 14 Jan 2016 14:54:39 +0100
    Subject: [PATCH] Squashed commits

    ---
     definitions/grib2/template.5.42.def          | 2 +-
     src/grib_accessor_class_data_ccsds_packing.c | 2 +-
     2 files changed, 2 insertions(+), 2 deletions(-)

    diff --git a/definitions/grib2/template.5.42.def b/definitions/grib2/template.5.42.def
    index a745d3f..39270ee 100644
    --- a/definitions/grib2/template.5.42.def
    +++ b/definitions/grib2/template.5.42.def
    @@ -15,7 +15,7 @@ include "template.5.original_values.def";
     unsigned[1] ccsdsFlags : dump;

     flagbit AEC_DATA_SIGNED_OPTION_MASK(ccsdsFlags,0)     = 0;
    -flagbit AEC_DATA_3BYTE_OPTION_MASK(ccsdsFlags,1)      = 0;
    +flagbit AEC_DATA_3BYTE_OPTION_MASK(ccsdsFlags,1)      = 1;
     flagbit AEC_DATA_MSB_OPTION_MASK(ccsdsFlags,2)        = 1;
     flagbit AEC_DATA_PREPROCESS_OPTION_MASK(ccsdsFlags,3) = 1;
     flagbit AEC_RESTRICTED_OPTION_MASK(ccsdsFlags,4)      = 0;
    diff --git a/src/grib_accessor_class_data_ccsds_packing.c b/src/grib_accessor_class_data_ccsds_packing.c
    index e81c307..60beee3 100644
    --- a/src/grib_accessor_class_data_ccsds_packing.c
    +++ b/src/grib_accessor_class_data_ccsds_packing.c
    @@ -269,7 +269,7 @@ static int  unpack_double(grib_accessor* a, double* val, size_t *len)
         */

         bits8 = ((bits_per_value + 7)/8)*8;
    -    size = n_vals * (bits_per_value + 7)/8;
    +    size = n_vals * ((bits_per_value + 7)/8);
         decoded = grib_context_buffer_malloc_clear(a->parent->h->context,size);
         if(!decoded) {
             err = GRIB_OUT_OF_MEMORY;
    --
    1.9.1
"""
from __future__ import print_function

import logging
import os
import subprocess
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from logging import info
from tempfile import NamedTemporaryFile

import numpy as np
try:
    from eccodes import codes_grib_new_from_file, codes_write
except ImportError:
    from gribapi import (grib_new_from_file as codes_grib_new_from_file,
                         grib_write as codes_write)

from utils import repack, gribs_match, EncodingError


class ExternalRepacker(object):

    """Repacks GRIBs using an external process."""

    repack_command = ("wgrib2 {input_file} -set_grib_type {packing_type} "
                      "-grib_out {output_file}")
    target_packing_type = "aec"
    round_trip_packing_type = "simple"

    def __init__(self, repack_command=None, target_packing_type=None,
                 round_trip_packing_type=None):
        if repack_command is not None:
            self.repack_command = repack_command
        if target_packing_type is not None:
            self.target_packing_type = target_packing_type
        if round_trip_packing_type is not None:
            self.round_trip_packing_type = round_trip_packing_type


def extract_gribs(input_file, extract_list, output_file):
    """
    Extract GRIBs at indices in extract_list from input_file to output_file.

    extract_list should be an iterable with boolean values corresponding to
    GRIBs in input_file. If extract contains True, the corresponding GRIB is
    appended to output_file.
    """
    if output_file is None:
        return
    i = 0
    with open(input_file) as infile:
        while True:
            grib = codes_grib_new_from_file(infile)
            if grib is None:
                break
            if extract_list[i]:
                with open(output_file, 'a') as output:
                    codes_write(grib, output)
            i += 1


def get_args():
    """Parse arguments from command line."""
    parser = ArgumentParser(description=__doc__[1:-1],
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", action="store_true", help="Verbose output")
    parser.add_argument("--external_repack_command",
                        help="External command to repack GRIBs. This should\n"
                             "be a quoted string with the arguments \n"
                             "'input_file', 'packing_type' and 'output_file'\n"
                             "in curly braces. Default:\n" +
                             ExternalRepacker.repack_command,
                        default=None)
    parser.add_argument("--target_packing_type",
                        help="Target packing type to check. Default:\n" +
                             ExternalRepacker.target_packing_type,
                        default=None)
    parser.add_argument("--round_trip_packing_type",
                        help="Packing type to check that the target packing "
                             "type is\n"
                             "decoded properly. Default:\n" +
                             ExternalRepacker.round_trip_packing_type,
                        default=None)
    parser.add_argument("--grib_api_errors",
                        help="File to write GRIBs to which don't match when\n"
                             "reencoded with GRIB API.")
    parser.add_argument("--external_errors",
                        help="File to write GRIBs to which don't match when\n"
                             "reencoded with external command.")
    parser.add_argument("grib", nargs="+", help="GRIB file to process")
    args = parser.parse_args()
    args.external_software = ExternalRepacker(args.external_repack_command,
                                              args.target_packing_type,
                                              args.round_trip_packing_type)
    return args


def main():
    args = get_args()
    if args.v:
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
    gribfiles = [os.path.realpath(x) for x in args.grib]
    ccsds = NamedTemporaryFile()
    external_ccsds = NamedTemporaryFile()
    round_trip = NamedTemporaryFile()

    for gribfile in gribfiles:
        info("Working with GRIBs in {}".format(gribfile))

        # Check encoding/decoding with ecCodes
        repack(gribfile, ccsds.name, "grid_ccsds")
        grib_api_matches = np.array(gribs_match(gribfile, ccsds.name))
        extract_gribs(gribfile, ~grib_api_matches, args.grib_api_errors)

        # Repeat with external command
        external = args.external_software
        subprocess.check_call(external.repack_command.format(
            input_file=gribfile,
            packing_type=external.target_packing_type,
            output_file=external_ccsds.name).split(" ")
        )
        subprocess.check_call(external.repack_command.format(
            input_file=external_ccsds.name,
            packing_type=external.round_trip_packing_type,
            output_file=round_trip.name).split(" ")
        )
        external_matches = np.array(gribs_match(gribfile, round_trip.name))
        extract_gribs(gribfile, ~external_matches, args.external_errors)

    return not any(grib_api_matches + external_matches)

if __name__ == '__main__':
    sys.exit(main())
