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

"""Tests for utility functions."""

from os import path
from tempfile import NamedTemporaryFile

from unittest import TestCase

from utils import confirm_packing_type, gribs_match, repack

DATA_DIR = path.join(path.dirname(path.realpath(__file__)), "test_data")
GRID_SIMPLE_COLLECTION = path.join(DATA_DIR, "grid_simple.grb")
GRID_SECOND_ORDER_COLLECTION = path.join(DATA_DIR, "grid_second_order.grb")
MIXED_GRIBS = path.join(DATA_DIR, "mixed.grb")
SHUFFLED_GRIBS = path.join(DATA_DIR, "shuffled.grb")


class TestUtils(TestCase):

    """Utils work as expected."""

    def test_confirm_packing_type(self):
        """Array returns as expected."""
        self.assertTrue(all(confirm_packing_type(GRID_SIMPLE_COLLECTION,
                                                 "grid_simple")))
        self.assertTrue(all(confirm_packing_type(GRID_SECOND_ORDER_COLLECTION,
                                                 "grid_second_order")))
        self.assertEqual([True, False, True],
                         confirm_packing_type(MIXED_GRIBS, "grid_simple"))

    def test_gribs_match(self):
        """GRIBs match and mismatch properly, errors are raised otherwise."""
        self.assertTrue(all(gribs_match(GRID_SIMPLE_COLLECTION,
                                        GRID_SECOND_ORDER_COLLECTION)))
        self.assertEqual([True, True, False, True, False],
                         gribs_match(GRID_SIMPLE_COLLECTION, SHUFFLED_GRIBS))
        self.assertEqual([True, False, False, False, False],
                          gribs_match(GRID_SIMPLE_COLLECTION, MIXED_GRIBS))

    def test_repack(self):
        """GRIBs are repacked and contain matching data with originals."""
        tmpfile = NamedTemporaryFile()
        repack(MIXED_GRIBS, tmpfile.name, "grid_second_order")
        self.assertTrue(all(gribs_match(tmpfile.name, MIXED_GRIBS)))
