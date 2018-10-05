import ldap3
import pytest

from flask import url_for

# from udata.auth import current_user
# from udata.core.user.factories import UserFactory
from udata.core.user.models import User
# from udata.utils import faker

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


@pytest.fixture
def ldap(app, mocker):
    manager = app.ldap3_login_manager
    manager.init_config(app.config)
    pool = manager._server_pool
    manager._server_pool = ldap3.Server('mock')

    def mock_make_connection(bind_user=None, bind_password=None, contextualise=True, **kwargs):
        print('make connection', bind_user, bind_password)
        connection = ldap3.Connection(manager._server_pool,
                                      user=bind_user, password=bind_password,
                                      client_strategy=ldap3.MOCK_SYNC,
                                      raise_exceptions=True)

        connection.strategy.add_entry(USER_DN, {
            'userPassword': PASSWORD,
            'givenName': FIRST_NAME,
            'sn': LAST_NAME,
            'mail': EMAIL,
            'objectClass': ['person'],
            'uid': UID,
        })

        connection.strategy.add_entry(BIND_USER_DN, {
            'userPassword': PASSWORD,
            'givenName': 'Mock',
            'sn': 'Mock',
            'mail': 'mock@test',
            'objectClass': ['person'],
        })
        if contextualise:
            manager._contextualise_connection(connection)
        return connection

    mocker.patch.object(manager, '_make_connection', side_effect=mock_make_connection)

    yield

    manager._server_pool = pool


def test_auth_with_email_and_password(client, ldap):
    post_url = url_for('ldap.login')

    response = client.post(post_url, {
        'username': EMAIL,
        'password': PASSWORD,
    })

    assert_redirects(response, url_for('site.home'))

    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.email == EMAIL
    assert user.first_name == FIRST_NAME
    assert user.last_name == LAST_NAME
    assert user.active


def test_auth_with_email_and_password_and_next(client, ldap):
    post_url = url_for('ldap.login')
    next_url = url_for('site.dashboard')

    response = client.post(post_url, {
        'username': EMAIL,
        'password': PASSWORD,
        'next': next_url,
    })

    assert_redirects(response, next_url)


@pytest.mark.options(LDAP_ALLOW_REMOTE_USER=True, LDAP_USER_SPNEGO_ATTR='uid')
def test_auth_with_remoute_user(client, ldap):
    page_url = url_for('site.home')

    response = client.get(page_url, headers={'REMOTE_USER': UID})

    assert200(response)

    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.email == EMAIL
    assert user.first_name == FIRST_NAME
    assert user.last_name == LAST_NAME
    assert user.active


def test_auth_with_invalid_password(client, ldap):
    post_url = url_for('ldap.login')

    response = client.post(post_url, {
        'username': EMAIL,
        'password': 'wrong-password',
    })

    assert200(response)  # Should display the formagain

    assert User.objects.count() == 0
