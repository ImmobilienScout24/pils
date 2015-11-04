from __future__ import print_function, absolute_import, division
from unittest import TestCase
import os
from pils import get_item_from_module


class PilsTests(TestCase):

    def test_raise_exception_when_module_could_not_be_loaded(self):
        self.assertRaises(Exception, get_item_from_module, "xyz", "")

    def test_raise_exception_when_item_not_in_module(self):
        self.assertRaises(Exception, get_item_from_module, "os", "systemTestXYZ")

    def test_get_item_from_module(self):
        self.assertEqual(os.system, get_item_from_module("os", "system"))

    def test_get_item_from_sub_module(self):
        self.assertEqual(os.path.join, get_item_from_module("os.path", "join"))
