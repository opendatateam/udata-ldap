# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from udata_ldap import settings as DEFAULTS
from udata_ldap.kerberos import KerberosManager


@pytest.fixture
def krb(app):
    for key, value in DEFAULTS.__dict__.items():
        if key.startswith('LDAP_'):
            app.config.setdefault(key, value)
    return KerberosManager(app)


@pytest.mark.parametrize('value,expected', (
    ('login@REALM', 'login'),
    ('login@REALM.ORG', 'login'),
    ('login@realm.org', 'login@realm.org'),
))
def test_strip_realm(krb, value, expected):
    assert krb.strip_realm(value) == expected
