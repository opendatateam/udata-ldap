# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from flask import url_for
from urlparse import urlparse, parse_qs

from udata.tests.helpers import assert_redirects

pytestmark = [
    pytest.mark.options(plugins=['ldap']),
]


def test_login_redirect_to_ldap_login(client):
    '''Login should redirect to the LDAP login page'''
    next_url = 'http://someurl/'
    message = 'You should log in'
    expected_url = url_for('ldap.login', next=next_url, message=message)

    response = client.get(url_for('security.login', next=next_url, message=message))

    assert_redirects(response, expected_url)

    response_url = urlparse(response.location)
    qs = parse_qs(response_url.query)

    assert qs['next'][0] == next_url
    assert qs['message'][0] == message


def test_login_redirect_to_ldap_with_unicode(client):
    '''Login should redirect to LDAP login page and support unicode'''
    next_url = 'http://someurl/é€'
    message = 'You should log in'
    expected_url = url_for('ldap.login', next=next_url, message=message)

    response = client.get(url_for('security.login', next=next_url, message=message))

    assert_redirects(response, expected_url)

    response_url = urlparse(response.location)
    qs = parse_qs(response_url.query)

    assert qs['next'][0].decode('utf-8') == next_url
    assert qs['message'][0] == message


def test_login_redirect_to_ldap_with_path_only(app, client):
    '''Login should redirect to ldap login and support unicode'''
    hostname = app.config['SERVER_NAME']
    next_url = '/é€'
    absolute_next_url = 'http://{0}{1}'.format(hostname, next_url)
    message = 'You should log in'
    expected_url = url_for('ldap.login', next=absolute_next_url, message=message)

    response = client.get(url_for('security.login', next=next_url, message=message))

    assert_redirects(response, expected_url)

    response_url = urlparse(response.location)
    qs = parse_qs(response_url.query)

    assert qs['next'][0].decode('utf-8') == absolute_next_url
    assert qs['message'][0] == message


@pytest.mark.frontend
def test_next_url_and_message_are_handled(client, templates):
    '''Login view should handle next and message parameters'''
    next_url = 'http://someurl/'
    message = 'You should log in'
    url = url_for('ldap.login', next=next_url, message=message)

    response = client.get(url)

    form = templates.get_context_variable('form')

    assert form.data['next'] == next_url
    assert message in response.data.decode('utf8')
