from __future__ import unicode_literals

'''
Default settings for udata-ldap
'''
import socket

LDAP_SERVER = None
# LDAP_SERVER_PORT = 389
LDAP_SSL = False
LDAP_BASE_DN = None
LDAP_USER_DN = None
LDAP_KERBEROS = False
LDAP_USER_LOGIN_ATTR = 'mail'
LDAP_KERBEROS_KEYTAB = None
LDAP_KERBEROS_SERVICE_NAME = 'HTTP'
LDAP_KERBEROS_SERVICE_HOSTNAME = socket.getfqdn()
LDAP_KERBEROS_SPNEGO = False

LDAP_USER_SPNEGO_ATTR = 'uid'
LDAP_ALLOW_REMOTE_USER = False
