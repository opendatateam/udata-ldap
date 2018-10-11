# -*- coding: utf-8 -*-
'''
udata LDAP

LDAP authentification for udata with optionnal Kerberos suppport.
'''
from __future__ import unicode_literals

__version__ = '0.3.2.dev'
__description__ = 'LDAP authentification for udata with optional Kerberos suppport.'


def init_app(app):
    from .ldap import manager
    from .views import bp, redirect_to_login

    app.register_blueprint(bp)
    app.view_functions['security.login'] = redirect_to_login

    manager.init_app(app)
