from __future__ import print_function, absolute_import, division


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
