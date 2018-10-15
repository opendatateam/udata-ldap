from __future__ import unicode_literals

'''
Default settings for udata-ldap
'''
import socket

LDAP_DEBUG = False
LDAP_KERBEROS = False
LDAP_USER_LOGIN_ATTR = 'mail'
LDAP_KERBEROS_KEYTAB = None
LDAP_KERBEROS_SERVICE_NAME = 'HTTP'
LDAP_KERBEROS_SERVICE_HOSTNAME = socket.getfqdn()
LDAP_KERBEROS_SPNEGO = False

LDAP_USER_FIRST_NAME_ATTR = 'givenName'
LDAP_USER_LAST_NAME_ATTR = 'sn'

LDAP_REMOTE_USER_ATTR = 'uid'
LDAP_ALLOW_REMOTE_USER = False
