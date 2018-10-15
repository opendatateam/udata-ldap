# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def get_ldap_value(data, key):
    '''Safely extract LDAP values'''
    data = data.get(key)
    if isinstance(data, (list, tuple)):
        return data[0] if len(data) else None
    else:
        return data
