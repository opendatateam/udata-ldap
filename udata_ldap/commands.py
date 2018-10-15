# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from click import echo, prompt
from flask_ldap3_login import AuthenticationResponseStatus

from udata.commands import cli, success, white, exit_with_error, header
from udata.utils import safe_unicode

from .ldap import manager


log = logging.getLogger(__name__)


@cli.group()
def ldap():
    '''LDAP related operations'''
    pass


@ldap.command()
def config():
    '''Display the LDAP configuration'''
    header('Current configuration')
    for key in sorted(manager.config):
        if key.startswith('LDAP_'):
            echo('{key}: {value}'.format(key=white(key),
                                         value=safe_unicode(manager.config[key])))


@ldap.command()
def check():
    '''Check the LDAP configuration'''
    bind_dn = manager.config.get('LDAP_BIND_USER_DN', None)
    if not bind_dn:
        exit_with_error('Missing LDAP_BIND_USER_DN setting')
    header('Trying to connect with bind user')
    try:
        who_am_i = manager.connection.extend.standard.who_am_i()
        success('Bind DN successfully connected')
        echo('Bind DN user is "{}"'.format(white(safe_unicode(who_am_i))))
    except Exception as e:
        exit_with_error('Unable to connect', e)

    header('Trying to authenticate an user')
    email = prompt(white('User email'))
    password = prompt(white('User password'), hide_input=True)
    result = manager.authenticate(email, password)
    if result.status == AuthenticationResponseStatus.success:
        success('User successfully connected')
        echo('Authenticated user is "{email} ({dn})"'.format(
            email=white(safe_unicode(result.user_id)),
            dn=white(safe_unicode(result.user_dn))
        ))
        echo('User has the following remote attributes:')
        for key, value in result.user_info.items():
            echo('{key}: {value}'.format(key=white(safe_unicode(key)),
                                         value=safe_unicode(value)))
        echo('Local user will be createdwith the following values:')
        for key, value in manager.extract_user_infos(result.user_info).items():
            echo('{key}: {value}'.format(key=white(safe_unicode(key)),
                                         value=safe_unicode(value)))
    else:
        exit_with_error('Unable to authenticate user "{0}"'.format(safe_unicode(email)))

    success('LDAP configuration is working')
