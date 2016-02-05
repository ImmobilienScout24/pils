from __future__ import print_function, absolute_import, division

import logging
import time
from functools import wraps


def get_item_from_module(module_name, item_name):
    """Load classes/modules/functions/... from given config"""
    try:
        module = __import__(module_name, fromlist=[item_name])
        item = getattr(module, item_name)
    except ImportError as error:
        message = 'Module "{modulename}" could not be loaded: {e}'
        raise Exception(message.format(
            modulename=module_name, e=error))
    except AttributeError as error:
        message = 'No item "{itemname}" in module "{modulename}": {e}'
        raise Exception(message.format(
            modulename=module_name,
            itemname=item_name,
                e=error))
    return item


def dict_is_subset(small_dict, big_dict):
    """Return True if small_dict is a subset of big_dict, else False

    For example, consider the dicts
        small = {'a':42}
        big = {'a':42, 'b': 43}
    small is a subset of big because every key in small also appears in the
    big and has the same value. The dict
        small2 = {'a': 43}
    is not a subset of big, because the values for 'a' differ.

    Recursive comparison is supported for dicts of dicts.

    One use case for this function is to filter USofA account data for accounts
    that match certain criteria. See unit tests for examples.
    """
    if not isinstance(big_dict, dict):
        # This may happen when the function recursively calls itself. Other
        # container types also support the 'in' operator, e.g.
        #   a = [42]
        #   42 in a
        # but
        #   a[42]
        # will cause an exception.
        return False

    for key, value in small_dict.items():
        if key not in big_dict:
            return False

        if isinstance(value, dict):
            if not dict_is_subset(value, big_dict[key]):
                return False
        else:
            if value != big_dict[key]:
                return False
    return True


def levelname_to_integer(level_name):
    """Translate human-readable log level name to an integer"""
    level_name = level_name.lower()
    level_translation = {'debug': logging.DEBUG, 'info': logging.INFO,
                         'warning': logging.WARNING, 'error': logging.ERROR,
                         'critical': logging.CRITICAL}
    if level_name not in level_translation:
        valid_levels = ", ".join(level_translation.keys())
        raise Exception('Log level "{0}" is invalid, use one of {1}.'.format(
                        level_name, valid_levels))
    return level_translation[level_name]

def retry(*args, **kwargs):
    """Retry the function call until it succeeds"""
    attempts = kwargs.pop('attempts', 3)
    delay = kwargs.pop('delay', 0)
    if kwargs:
        raise Exception("Unknown kwargs given: " + ", ".join(kwargs.keys()))

    def retry_decorator(old_function):
        """Retry the function call until it succeeds"""
        @wraps(old_function)
        def call_with_retry(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return old_function(*args, **kwargs)
                except Exception:
                    if attempt == attempts - 1:
                        raise
                    time.sleep(delay)
        return call_with_retry

    if args:
        if len(args) > 1:
            raise Exception("You cannot pass more than 1 argument to retry()")
        return retry_decorator(args[0])

    return retry_decorator

