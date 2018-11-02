from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from jinja2 import Environment, FileSystemLoader
from django.utils.crypto import get_random_string


def create_secret_key():
    return get_random_string(50)


class FilterModule(object):
    """ adds generate random secret key filter """
    def filters(self):
        return {
            # filter map
            'create_secret_key': create_secret_key
        }
