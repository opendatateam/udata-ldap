# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask_security.forms import NextFormMixin, password_required
from wtforms import PasswordField

from udata.forms import Form, fields, validators
from udata.i18n import lazy_gettext as _


class LoginForm(Form, NextFormMixin):
    username = fields.StringField(_('Email Address'), validators=[validators.required()])
    password = PasswordField(_('Password'), validators=[password_required])
    remember = fields.BooleanField(_('Remember Me'))
