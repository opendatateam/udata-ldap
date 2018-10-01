import pytest

from udata_ldap import init_app


@pytest.fixture
def app(app):
    init_app(app)
    return app
