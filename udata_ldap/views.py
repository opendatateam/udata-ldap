# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from flask import current_app, flash, request, url_for, redirect
from flask.views import MethodView

from flask_security.utils import login_user

from udata import theme
from udata.i18n import I18nBlueprint, gettext as _

from udata.core.user.models import datastore

from .forms import LoginForm
from .ldap import manager
from .utils import get_ldap_value

from flask_ldap3_login import AuthenticationResponseStatus

bp = I18nBlueprint('ldap', __name__, url_prefix='/ldap',
                   template_folder='templates')

log = logging.getLogger(__name__)


@bp.before_app_request
def check_remote_user():
    if not current_app.config.get('LDAP_ALLOW_REMOTE_USER', False):
        return
    remote_user = request.headers.get('REMOTE_USER')
    if not remote_user:
        return
    data = manager.get_trusted_user_infos(remote_user, manager.config.get('LDAP_REMOTE_USER_ATTR'))
    if data:
        email = get_ldap_value(data, 'mail')
        user = datastore.find_user(email=email)
        if user is None:
            user = datastore.create_user(
                active=True,
                **manager.extract_user_infos(data)
            )
        else:
            user.modify(**manager.extract_user_infos(data))
        login_user(user)


def redirect_to_login():
    params = {}
    if 'next' in request.args:
        next_url = request.args['next']
        if next_url.startswith('/') and not next_url.startswith('//'):
            next_url = '{0}://{1}{2}'.format(request.scheme,
                                             current_app.config['SERVER_NAME'],
                                             next_url)
        params['next'] = next_url
    if 'message' in request.args:
        params['message'] = request.args['message']
    return redirect(url_for('ldap.login', **params))


@bp.route('/login', endpoint='login')
class LoginView(MethodView):
    def get(self):
        params = {}
        if 'next' in request.args:
            params['next'] = request.args['next']

        if 'message' in request.args and not request.is_json:
            flash(request.args['message'])

        return theme.render('ldap/login.html', form=LoginForm(**params))

    def post(self):
        form = LoginForm(request.form)
        error = None
        if form.validate():
            username = form.username.data
            password = form.password.data

            result = manager.authenticate(username, password)

            if result.status == AuthenticationResponseStatus.success:
                if manager.verbose:
                    log.info('Found remote user %s', result.user_id)
                user = datastore.find_user(email=result.user_id)
                if user is None:
                    user = datastore.create_user(
                        active=True,
                        **manager.extract_user_infos(result.user_info)
                    )
                else:
                    user.modify(**manager.extract_user_infos(result.user_info))
                if login_user(user, remember=form.remember.data):
                    next_url = form.next.data or url_for('site.home')
                    return redirect(next_url)
                else:
                    error = _('This user has been deactived')
            error = _('Invalid credentials')
        return theme.render('ldap/login.html', form=form, error=error)


@bp.route('/negociate')
def negociate():
    username = manager.kerberos.negociate()
    if username:
        log.info('Initialization complete, fetching user details for %s', username)
        data = manager.get_trusted_user_infos(manager.kerberos.strip_realm(username),
                                              manager.config.get('LDAP_REMOTE_USER_ATTR'))
        if data:
            email = get_ldap_value(data, 'mail')
            if manager.verbose:
                log.info('Found remote user %s', email)
            user = datastore.find_user(email=email)
            if user is None:
                user = datastore.create_user(
                    active=True,
                    **manager.extract_user_infos(data)
                )
            else:
                user.modify(**manager.extract_user_infos(data))
            if login_user(user):
                next_url = request.args.get('next', url_for('site.home'))
                return redirect(next_url)
            else:
                flash(_('This user has been deactived'))
                return redirect(url_for('site.home'))
        else:
            return redirect(url_for('ldap.login', message=_('Invalid credentials')))

    error = {'code': 401}
    return theme.render('ldap/negociate.html', error=error), 401, {'WWW-Authenticate': 'Negotiate'}
