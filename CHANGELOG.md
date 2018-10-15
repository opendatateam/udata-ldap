# Changelog

## Current (in progress)

- Fix some console encoding error
- Fix LDAP values extraction

## 0.3.1 (2018-10-11)

- Renamed `LDAP_USER_SPNEGO_ATTR` into `LDAP_REMOTE_USER_ATTR` for consistency
- Fix login form using SPNEGO attribute for login

## 0.3.0 (2018-10-09)

- Display errors on login form
- Force email into the login form
- Fix encoding errors in ldap commands
- Update user on login
- Start handling errors on negociate view
- Display a page when trying automatic login wihtout credentials
- Adds translations

## 0.2.1 (2018-10-08)

- Fix the "automatic login" link
- More logging

## 0.2.0

- More tests
- Hide debug log unless `LDAP_DEBUG = True`
- Remove buggy default `LDAP_*` settings

## 0.1.0

Initial release
