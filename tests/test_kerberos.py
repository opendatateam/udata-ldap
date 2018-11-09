# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from udata_ldap.kerberos import KerberosManager


@pytest.fixture
def krb(app):
    return KerberosManager(app)


@pytest.mark.parametrize('value,expected', (
    ('login@REALM', 'login'),
    ('login@REALM.ORG', 'login'),
    ('login@realm.org', 'login@realm.org'),
))
def test_strip_realm(krb, value, expected):
    assert krb.strip_realm(value) == expected
