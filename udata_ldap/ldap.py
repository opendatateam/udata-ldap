# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from flask import current_app
from flask_ldap3_login import LDAP3LoginManager

from . import settings as DEFAULTS
from .utils import get_ldap_value


class LDAPManager(LDAP3LoginManager):
    '''
    Manage all LDAP exchanges
    '''
    # Map user attribute to config keys
    USER_FIELDS = {
        'first_name': 'LDAP_USER_FIRST_NAME_ATTR',
        'last_name': 'LDAP_USER_LAST_NAME_ATTR',
        'email': 'LDAP_USER_LOGIN_ATTR',
    }

    def init_app(self, app):
        super(LDAPManager, self).init_app(app)
        self.verbose = self.config['DEBUG'] or self.config['LDAP_DEBUG'] or self.config['TESTING']
        self.init_logging(app)
        self.init_kerberos(app)

    def init_logging(self, app):
        with app.app_context():
            level = logging.DEBUG if self.verbose else current_app.logger.level
        for name in 'flask_ldap3_login', 'udata_ldap':
            logger = logging.getLogger(name)
            logger.setLevel(level)

    def init_config(self, config):
        # Set default before flask-ldap3 because only first dict.setdefault is remembered
        for key, value in DEFAULTS.__dict__.items():
            if key.startswith('LDAP_'):
                self.config.setdefault(key, value)

        super(LDAPManager, self).init_config(config)

    def init_kerberos(self, app):
        self.kerberos = None
        if app.config.get('LDAP_KERBEROS_KEYTAB'):
            from .kerberos import KerberosManager
            self.kerberos = KerberosManager(app)

    def get_trusted_user_infos(self, identifier, attribute=None, _connection=None):
        '''
        Extract infos from a trusted user.

        :param string identifier: The value on which the user is queried.
        :param string attribute: The attribute against which the user is queried
                                 (defaults to `LDAP_USER_LOGIN_ATTR`)
        '''
        attribute = attribute or self.config.get('LDAP_USER_LOGIN_ATTR')
        ldap_filter = '(&({0}={1}){2})'.format(
            attribute,
            identifier,
            self.config.get('LDAP_USER_OBJECT_FILTER')
        )

        return self.get_object(
            dn=self.full_user_search_dn,
            filter=ldap_filter,
            attributes=self.config.get("LDAP_GET_USER_ATTRIBUTES"),
            _connection=_connection,
        )

    def extract_user_infos(self, data):
        return dict(
            (field, get_ldap_value(data, self.config[key]))
            for field, key in self.USER_FIELDS.items()
        )


manager = LDAPManager()
