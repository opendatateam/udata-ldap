# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import pytest
import requests

from flask import url_for
from udata.core.user.models import User
from udata.tests.helpers import assert_redirects, assert200

BASE_DN = 'dc=test'
BIND_USER_DN = 'cn=mock,{}'.format(BASE_DN)

USER_DN = 'cn=user,{}'.format(BASE_DN)
FIRST_NAME = 'John'
LAST_NAME = 'Doe'
EMAIL = 'coucou@cmoi.fr'
# Mock LDAP will reject any other password
PASSWORD = 'only-good-password'
UID = 1234


pytestmark = [
    pytest.mark.frontend,
    pytest.mark.usefixtures('clean_db'),
    pytest.mark.options(plugins=['ldap'],
                        LDAP_BASE_DN=BASE_DN,
                        LDAP_USER_DN='',
                        LDAP_BIND_USER_DN=BIND_USER_DN,
                        LDAP_BIND_USER_PASSWORD=PASSWORD),
]


class FreeIPA(object):
    '''A dead simple freeipa client fortesting purpose'''
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password
        self.log = logging.getLogger(__name__)
        self.session = requests.Session()
        self.logged_in = False

    @property
    def base_url(self):
        return 'https://{0}/ipa'.format(self.server)

    @property
    def session_url(self):
        return '{}/session'.format(self.base_url)

    @property
    def rpc_url(self):
        return '{}/json'.format(self.session_url)

    def login(self):
        login_url = '{0}/login_password'.format(self.session_url)
        '''
             -H referer:https://$IPAHOSTNAME/ipa \
          -H "Content-Type:application/ x-www-form-urlencoded" \
          -H "Accept:text/plain"\
          -c $COOKIEJAR -b $COOKIEJAR \
          --cacert /etc/ipa/ca.crt \
          --data "user=$username&password=$password" \
          -X POST https://$IPAHOSTNAME/ipa/session/login_password
        '''
        header = {
            'referer': self.base_url,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
        }
        data = {'user': self.user, 'password': self.password}
        rv = self.session.post(login_url, headers=header, data=data, verify=False)

        if rv.status_code != 200:
            self.log.warning('Failed to log {0} in to {1}'.format(
                self.user,
                self.server)
            )
            return None
        self.log.info('Successfully logged in as {0}'.format(self.user))
        # set login_user for use when changing password for self
        self.logged_in = True
        print('response', rv, rv.status_code)
        return rv

    def rpc(self, method, *args, **kwargs):
        header = {
            'referer': self.base_url,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        data = {
            'id': 0,
            'method': method,
            'params': [args, kwargs]
        }

        self.log.debug('Making {0} request to {1}'.format(method, self.rpc_url))

        if not self.logged_in:
            self.login()

        resp = self.session.post(
                self.rpc_url, headers=header,
                data=json.dumps(data),
                verify=False
        )
        if resp.status_code != 200:
            self.log.warning('Failed to execute {method}. Reponse is {resp.status_code}: {resp.text}'.format(**locals()))
            resp.raise_for_status()
        return resp.json()

    def config_show(self):
        return self.rpc('config_show', all=True)


@pytest.fixture
def krb():
    server_name = os.environ.get('IPA_SERVER_HOSTNAME', 'ldap.test')
    print('server_name', server_name)
    ipa = FreeIPA(server_name, 'admin', 'password')
    yield ipa


def test_krb(krb):
    from pprint import pprint
    print('config')
    pprint(krb.config_show())
    # print('REALM:', krb.realm)
    # print('hostname:', krb.hostname)
    # print(dir(krb))
    raise ValueError()


# def test_auth_with_email_and_password(client, krb):
#     post_url = url_for('ldap.login')

#     response = client.post(post_url, {
#         'username': EMAIL,
#         'password': PASSWORD,
#     })

#     assert_redirects(response, url_for('site.home'))

#     assert User.objects.count() == 1

#     user = User.objects.first()
#     assert user.email == EMAIL
#     assert user.first_name == FIRST_NAME
#     assert user.last_name == LAST_NAME
#     assert user.active
