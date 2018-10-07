import pytest

from udata_ldap import init_app


@pytest.fixture
def app(app):
    app.config['LDAP_HOST'] = 'ldap.test'
    init_app(app)
    return app
