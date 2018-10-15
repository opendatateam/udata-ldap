# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from udata_ldap import utils as u


class GetLdapValueTest:
    @pytest.mark.parametrize('value', ['test', 42])
    def test_single_value(self, value):
        data = {'key': value}
        assert u.get_ldap_value(data, 'key') == value

    @pytest.mark.parametrize('value', ['test', 42])
    def test_single_value_in_list(self, value):
        data = {'key': [value]}
        assert u.get_ldap_value(data, 'key') == value

    @pytest.mark.parametrize('value', ['test', 42])
    def test_multiple_values_in_list(self, value):
        data = {'key': [value, 'KO']}
        assert u.get_ldap_value(data, 'key') == value

    def test_empty_list(self):
        data = {'key': []}
        assert u.get_ldap_value(data, 'key') is None

    def test_none(self):
        data = {'key': None}
        assert u.get_ldap_value(data, 'key') is None

    def test_missing_key(self):
        assert u.get_ldap_value({}, 'key') is None
