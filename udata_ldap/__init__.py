# -*- coding: utf-8 -*-
'''
udata LDAP

LDAP authentification for udata with optionnal Kerberos suppport.
'''
from __future__ import unicode_literals

import logging

__version__ = '0.1.0'
__description__ = 'LDAP authentification for udata with optionnal Kerberos suppport.'


def init_app(app):
    from .ldap import manager
    from .views import bp, redirect_to_login

    app.register_blueprint(bp)
    app.view_functions['security.login'] = redirect_to_login

    config = app.extensions['ldap'] = {}

    manager.init_app(app)

    logging.getLogger('flask_ldap3_login').setLevel(logging.DEBUG)

    # if 'KRB5_KTNAME' not in environ:
    #     app.logger.warn("Kerberos: set KRB5_KTNAME to your keytab file")
    # else:
    #     try:
    #         principal = kerberos.getServerPrincipalDetails(service, hostname)
    #     except kerberos.KrbError as exc:
    #         app.logger.warn("Kerberos: %s" % exc.message[0])
    #     else:
    #         app.logger.info("Kerberos: server is %s" % principal)

    # store = {'ccache': 'FILE:/some/ccache/file', 'keytab':'/etc/some.keytab' }
    if app.config.get('LDAP_KERBEROS_KEYTAB'):
        import gssapi
        store = {'keytab': app.config['LDAP_KERBEROS_KEYTAB']}
        service_name = app.config['LDAP_KERBEROS_SERVICE_NAME']
        hostname = app.config['LDAP_KERBEROS_SERVICE_HOSTNAME']
        principal = '{}@{}'.format(service_name, hostname)
        name = gssapi.Name(principal, gssapi.NameType.hostbased_service)

        config['creds'] = gssapi.Credentials(name=name, usage='accept', store=store)
