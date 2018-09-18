import pytest


from udata.auth import current_user
from udata.core.user.factories import UserFactory
from udata.core.user.models import User
from udata.utils import faker


pytestmark = [
    pytest.mark.usefixtures('clean_db'),
    pytest.mark.options(plugins=['ldap']),
]


def test_extract_remote_user_and_create_user(client):
    email = faker.email()
    with client:
        client.get('/', headers={'REMOTE_USER': email})

        assert User.objects.count() == 1

        user = User.objects.first()

        assert current_user.is_authenticated
        assert current_user == user

    assert user.email == email


def test_extract_remote_user_and_find_user(client):
    user = UserFactory()

    with client:
        client.get('/', headers={'REMOTE_USER': user.email})

        assert User.objects.count() == 1

        assert current_user.is_authenticated
        assert current_user == user


def test_default_extract_names(client):
    email = 'first_name.last_name@domain.com'
    with client:
        client.get('/', headers={'REMOTE_USER': email})

        assert User.objects.count() == 1

        user = User.objects.first()

        assert current_user.is_authenticated
        assert current_user == user

    assert user.first_name == 'first_name'
    assert user.last_name == 'last_name'
