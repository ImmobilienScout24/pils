from __future__ import print_function, absolute_import, division

from unittest import TestCase
import logging
import os
import time

import mock

from pils import (get_item_from_module, dict_is_subset, levelname_to_integer,
                  retry)


class PilsTests(TestCase):
    def test_raise_exception_when_module_could_not_be_loaded(self):
        self.assertRaises(Exception, get_item_from_module, "xyz", "")

    def test_raise_exception_when_item_not_in_module(self):
        self.assertRaises(Exception, get_item_from_module, "os", "systemTestXYZ")

    def test_get_item_from_module(self):
        self.assertEqual(os.system, get_item_from_module("os", "system"))

    def test_get_item_from_sub_module(self):
        self.assertEqual(os.path.join, get_item_from_module("os.path", "join"))


    def test_empty_dict_is_always_a_subset(self):
        self.assertEqual(dict_is_subset({}, {}), True)
        self.assertEqual(dict_is_subset({}, {'foo': 'bar'}), True)

    def test_flat_dicts_that_are_subsets(self):
        small = {'a': 42}
        big = {'a':42, 'b': 43}
        self.assertEqual(dict_is_subset(small, big), True)
        self.assertEqual(dict_is_subset(big, big), True)

    def test_flat_dicts_that_are_not_subsets(self):
        small = {'a': 43}
        small2 = {'b': 42}
        small3 = {'a': '42'}
        small4 = {'c': 42}
        big = {'a':42, 'b': 43}
        self.assertEqual(dict_is_subset(small, big), False)
        self.assertEqual(dict_is_subset(small2, big), False)
        self.assertEqual(dict_is_subset(small3, big), False)
        self.assertEqual(dict_is_subset(small4, big), False)

    def test_recursive_dicts(self):
        """This is useful for filtering USofA data"""
        small = {
            'account1': {
                'owner': 'me'
            }
        }
        small2 = {
            'account1': {
                'owner': 'somebodyelse'
            }
        }
        small3 = {
            'missing_in_big': {
                'foo': 42
            }
        }
        big = {
            'account1': {
                'id': 42,
                'owner': 'me',
            },
            'account2': {
                'id': 43,
                'owner': 'notme'
            }
        }

        self.assertEqual(dict_is_subset(big, big), True)
        self.assertEqual(dict_is_subset(small, big), True)
        self.assertEqual(dict_is_subset(small2, big), False)
        self.assertEqual(dict_is_subset(small3, big), False)

    def test_recursing_meets_non_dict_container(self):
        small = {
            'foo': {'bar': 42}
        }
        big = {
            'foo': ['bar']
        }
        self.assertEqual(dict_is_subset(small, big), False)

    def test_levelname_to_integer_knows_all_loglevels(self):
        translated_level = levelname_to_integer('debug')
        self.assertEqual(translated_level, logging.DEBUG)
        translated_level = levelname_to_integer('info')
        self.assertEqual(translated_level, logging.INFO)
        translated_level = levelname_to_integer('warning')
        self.assertEqual(translated_level, logging.WARNING)
        translated_level = levelname_to_integer('error')
        self.assertEqual(translated_level, logging.ERROR)
        translated_level = levelname_to_integer('critical')
        self.assertEqual(translated_level, logging.CRITICAL)

    def test_case_insensitive_input_levelname_to_integer(self):
        translated_level = levelname_to_integer('DeBuG')
        self.assertEqual(translated_level, logging.DEBUG)

    def test_levelname_to_integer_excepts_on_invalid_level(self):
        self.assertRaises(Exception, levelname_to_integer, "invalidloglevel")

    def test_retry_passes_return_value(self):
        my_function = retry(lambda: 42)
        self.assertEqual(my_function(), 42)

    def test_retry_passes_exceptions(self):
        def helper():
            raise Exception("some exception")

        retry_helper = retry(helper)

        self.assertRaises(Exception, retry_helper)

    def test_retry_actually_retries(self):
        helper = mock.Mock()
        helper.side_effect = [Exception, 42]
        helper.__name__ = "workaround for mock failure"

        retry_helper = retry(helper)

        self.assertEqual(retry_helper(), 42)

    def test_retry_uses_the_attempts_parameter(self):
        helper = mock.Mock()
        helper.side_effect = [Exception, 42]
        helper.__name__ = "workaround for mock failure"

        retry_helper = retry(helper, attempts=1)
        self.assertRaises(Exception, retry_helper)

    def test_retry_uses_delay_parameter(self):
        helper = mock.Mock()
        helper.side_effect = [Exception, 42]
        helper.__name__ = "workaround for mock failure"

        retry_helper = retry(helper, delay=1)

        start = time.time()
        self.assertEqual(retry_helper(), 42)
        stop = time.time()

        delta = stop - start
        self.assertGreater(delta, 1)

