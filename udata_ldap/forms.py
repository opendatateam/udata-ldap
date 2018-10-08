# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask_security.forms import NextFormMixin, password_required
from wtforms import PasswordField
from wtforms.fields.html5 import EmailField as WtEmailField

from udata.forms import Form, fields, validators
from udata.i18n import lazy_gettext as _


class EmailField(fields.FieldHelper, WtEmailField):
    pass


class LoginForm(Form, NextFormMixin):
    username = EmailField(_('Email Address'), validators=[validators.required()])
    password = PasswordField(_('Password'), validators=[password_required])
    remember = fields.BooleanField(_('Remember Me'))
