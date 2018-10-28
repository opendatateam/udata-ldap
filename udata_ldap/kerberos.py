# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import gssapi
import logging
import os

from flask import request

log = logging.getLogger(__name__)


class KerberosManager(object):
    '''
    Manage Kerberos names, credentials, security context
    and common tasks
    '''
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

    def accept_security_context(self):
        credentials = gssapi.Credentials(name=self.name, usage='accept', store=self.store)
        return gssapi.SecurityContext(creds=credentials, usage='accept')

    def initiate_security_context(self):
        log.debug('Initialize security context for %s', self.canonical_name)
        credentials = gssapi.Credentials(name=self.name, usage='initiate', store=self.store)
        return gssapi.SecurityContext(name=self.name, usage='initiate', creds=credentials)

    def check_keytab(self):
        '''
        Check keytab validity.
        '''
        if not os.path.exists(self.keytab):
            log.error('Keytab %s not found', self.keytab)
            return False
        else:
            log.info('Using keytab %s', self.keytab)
        ctx = self.initiate_security_context()
        input_token = None
        while not ctx.complete:
            output_token = ctx.step(input_token)

    def negociate(self):
        '''
        Perform a SPNEGO negociation.

        :return: the initiator name on success, None otherwise
        '''
        if request.headers.get('Authorization', '').startswith('Negotiate '):
            in_token = base64.b64decode(request.headers['Authorization'][10:])

            ctx = self.accept_security_context()

            ctx.step(in_token)
            log.info('Initialized security context for %s on target %s using %s',
                     ctx.initiator_name, ctx.target_name, ctx.mech)

            if ctx.complete:
                return ctx._inquire(initiator_name=True).initiator_name
