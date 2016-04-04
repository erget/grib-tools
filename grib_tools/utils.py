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

"""Utilities for repacking GRIBs and testing for identical contents."""

import numpy as np
from eccodes import (codes_grib_new_from_file,
                     codes_get_values,
                     codes_clone,
                     codes_set_values,
                     codes_set,
                     codes_write,
                     codes_release,
                     codes_get,
                     CodesInternalError)


class EncodingError(Exception):
    """An error occurred during encoding or decoding."""


def confirm_packing_type(gribfile, packing_type):
    """Confirm that gribfile contains only GRIBs with specified packingType."""
    comparisons = []
    with open(gribfile) as infile:
        while True:
            gid = codes_grib_new_from_file(infile)
            if gid is None:
                break
            encoded_type = codes_get(gid, "packingType")
            codes_release(gid)
            comparisons.append(encoded_type == packing_type)
    return comparisons


def repack(input_file, outfile, packing_type):
    """Repack infile with packing_type, write result to outfile."""
    with open(input_file) as infile:
        while True:
            in_gid = codes_grib_new_from_file(infile)
            if in_gid is None:
                break
            payload = codes_get_values(in_gid)
            clone_id = codes_clone(in_gid)
            codes_set(clone_id, "packingType", packing_type)
            codes_set_values(clone_id, payload)
            with open(outfile, "a") as output:
                codes_write(clone_id, output)
            codes_release(clone_id)
            codes_release(in_gid)
    if not confirm_packing_type(outfile, packing_type):
        raise EncodingError("CCSDS encoding silently failed.")


def gribs_match(left, right):
    """Check if GRIBs in both input files store the same data."""
    comparisons = []
    with open(left) as a, open(right) as b:
        while True:
            a_gid = codes_grib_new_from_file(a)
            if a_gid is None:
                break
            b_gid = codes_grib_new_from_file(b)
            packing_errors = [0]
            try:
                packing_errors.append(codes_get(a_gid, "packingError"))
                packing_errors.append(codes_get(b_gid, "packingError"))
            except CodesInternalError:
                pass
            tolerance = max(packing_errors)
            a_values = codes_get_values(a_gid)
            b_values = codes_get_values(b_gid)
            comparisons.append(np.allclose(a_values, b_values, atol=tolerance))
    return comparisons
