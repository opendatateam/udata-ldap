# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import gssapi
import os
import logging

log = logging.getLogger(__name__)


class KerberosManager(object):
    def __init__(self, app):
        self.verbose = app.config['DEBUG'] or app.config['LDAP_DEBUG'] or app.config['TESTING']
        # os.environ['KRB5_KTNAME'] = app.config['LDAP_KERBEROS_KEYTAB']
        # os.environ['KRB5_CLIENT_KTNAME'] = app.config['LDAP_KERBEROS_KEYTAB']
        self.keytab = app.config['LDAP_KERBEROS_KEYTAB']
        self.store = {'keytab': self.keytab, 'keytab_client': self.keytab}
        self.service_name = app.config['LDAP_KERBEROS_SERVICE_NAME']
        self.hostname = app.config['LDAP_KERBEROS_SERVICE_HOSTNAME']
        self.principal = '{}@{}'.format(self.service_name, self.hostname)
        self.name = gssapi.Name(self.principal, gssapi.NameType.hostbased_service)
        self.canonical_name = self.name.canonicalize(gssapi.MechType.kerberos)
        app.extensions['kerberos'] = self

    @property
    def security_context(self):
        return gssapi.SecurityContext(creds=self.credentials, usage='accept')

    def accept_security_context(self):
        credentials = gssapi.Credentials(name=self.name, usage='accept', store=self.store)
        return gssapi.SecurityContext(creds=credentials, usage='accept')

    def initiate_security_context(self):
        log.debug('Initialize security context for %s', self.canonical_name)
        credentials = gssapi.Credentials(name=self.name, usage='initiate', store=self.store)
        return gssapi.SecurityContext(name=self.name, usage='initiate', creds=credentials)

    def check_keytab(self):
        if not os.path.exists(self.keytab):
            log.error('Keytab %s not found', self.keytab)
            return False
        else:
            log.info('Using keytab %s', self.keytab)
        ctx = self.initiate_security_context()
        input_token = None
        while not ctx.complete:
            output_token = ctx.step(input_token)

