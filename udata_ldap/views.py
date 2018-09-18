# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import gssapi

from flask import current_app, request, Response, url_for, redirect
from flask.views import MethodView

from flask_security.utils import login_user

from udata import theme
from udata.i18n import I18nBlueprint

from udata.core.user.models import datastore

from .forms import LoginForm
from .ldap import manager

from flask_ldap3_login import AuthenticationResponseStatus

bp = I18nBlueprint('ldap', __name__, url_prefix='/ldap',
                   template_folder='templates',)


@bp.before_app_request
def check_remote_user():
    if not current_app.config.get('LDAP_ALLOW_REMOTE_USER', False):
        return
    remote_user = request.headers.get('REMOTE_USER')
    if not remote_user:
        return
    data = manager.get_trusted_user_infos(remote_user)
    if data:
        user = datastore.find_user(email=data['mail'][0])
        if not user:
            user = datastore.create_user(
                active=True,
                **manager.extract_user_infos(data)
            )
        login_user(user)
        return redirect(url_for('site.home'))


def redirect_to_login():
    return redirect(url_for('ldap.login'))


@bp.route('/login', endpoint='login')
class LoginView(MethodView):
    def get(self):
        return theme.render('ldap/login.html', form=LoginForm())

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data

            result = manager.authenticate(username, password)

            if result.status == AuthenticationResponseStatus.success:
                user = datastore.find_user(email=result.user_id)
                if not user:
                    user = datastore.create_user(
                        active=True,
                        **manager.extract_user_infos(result.user_info)
                    )
                login_user(user)
                next_url = form.next.data or url_for('site.home')
                return redirect(next_url)
        return theme.render('ldap/login.html', form=form)


@bp.route('/negociate')
def negociate():
    if request.headers.get('Authorization', '').startswith('Negotiate '):
        in_token = base64.b64decode(request.headers['Authorization'][10:])

        try:
            creds = current_app.extensions['ldap']['creds']
        except KeyError:
            raise RuntimeError('gssapi not configured for this app')

        ctx = gssapi.SecurityContext(creds=creds, usage='accept')

        out_token = ctx.step(in_token)

        if ctx.complete:
            username = str(ctx._inquire(initiator_name=True).initiator_name)
            data = manager.get_trusted_user_infos(username)
            if data:
                user = datastore.find_user(email=data['mail'][0])
                if not user:
                    user = datastore.create_user(
                        active=True,
                        **manager.extract_user_infos(data)
                    )
                login_user(user)
                return redirect(url_for('site.home'))

            next_url = request.args['next'] if 'next' in request.args else url_for('site.home')
            return redirect(next_url)

    return Response(
        status=401,
        headers={'WWW-Authenticate': 'Negotiate'},
    )
