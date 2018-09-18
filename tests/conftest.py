import pytest

from udata_ldap import init_app

# from udata import settings
# from udata.app import create_app


# pytestmark = pytest.mark.options(PLUGINS=['kerberos'])

# class KerberosSettings(settings.Testing):
#     PLUGINS = ['kerberos']


@pytest.fixture
def app(app):
    init_app(app)
    # from udata.app import register_features
    # register_features(app)
    # app = create_app(settings.Defaults, override=KerberosSettings)
    return app
