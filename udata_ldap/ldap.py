# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from flask import current_app
from flask_ldap3_login import LDAP3LoginManager

from . import settings as DEFAULTS
from .utils import get_ldap_value


class LDAPManager(LDAP3LoginManager):
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
        self.krb_config = {}
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
        if app.config.get('LDAP_KERBEROS_KEYTAB'):
            import gssapi
            config = app.extensions['ldap'] = {}
            store = {'keytab': app.config['LDAP_KERBEROS_KEYTAB']}
            service_name = app.config['LDAP_KERBEROS_SERVICE_NAME']
            hostname = app.config['LDAP_KERBEROS_SERVICE_HOSTNAME']
            principal = '{}@{}'.format(service_name, hostname)
            name = gssapi.Name(principal, gssapi.NameType.hostbased_service)

            config['name'] = name
            config['credentials'] = gssapi.Credentials(name=name, usage='accept', store=store)

    @property
    def kerberos_name(self):
        if not current_app.config.get('LDAP_KERBEROS_KEYTAB'):
            raise RuntimeError('Kerberos not configured for this app')
        try:
            return current_app.extensions['ldap']['name']
        except KeyError:
            raise RuntimeError('Kerberos/GSSAPI not configured for this app')

    @property
    def kerberos_credentials(self):
        if not current_app.config.get('LDAP_KERBEROS_KEYTAB'):
            raise RuntimeError('Kerberos not configured for this app')
        try:
            return current_app.extensions['ldap']['credentials']
        except KeyError:
            raise RuntimeError('Kerberos/GSSAPI not configured for this app')

    @property
    def kerberos_security_context(self):
        if not current_app.config.get('LDAP_KERBEROS_KEYTAB'):
            raise RuntimeError('Kerberos not configured for this app')
        import gssapi

        return gssapi.SecurityContext(creds=self.kerberos_credentials, usage='accept')

    def get_trusted_user_infos(self, identifier, attribute=None, _connection=None):
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
