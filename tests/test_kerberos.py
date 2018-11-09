# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from udata_ldap.ldap import manager


@pytest.fixture
def krb(app):
    return manager.kerberos


@pytest.mark.parametrize('value,expected', (
    ('login@REALM', 'login'),
    ('login@REALM.ORG', 'login'),
    ('login@realm.org', 'login@realm.org'),
))
def test_strip_realm(krb, value, expected):
    assert krb.strip_realm(value) == expected
