# udata-ldap

LDAP authentification for udata with optionnal Kerberos suppport.

## Requirements

To use LDAP only authentication, you only need the `udata-ldap` extension.
To use `SASL` and `SPNEGO`, you need a functionnal kerberos client environnement.
On debian, you can install the requirements using:

```bash
apt-get install krb5-config krb5-user libkrb5-dev
```

## Usage

Install the plugin package in you udata environement:

```bash
pip install udata-ldap
```

Then activate it in your `udata.cfg`:

```python
PLUGINS = ['ldap']
```

**NB**: if using Kerberos SASL and/or SPNEGO, install it with:

```bash
pip install udata-ldap[kerberos]
```

## Configuration

`udata-ldap` makes use of [`flask-ldap3-login`](https://flask-ldap3-login.readthedocs.io/en/latest/index.html) and so use the same parameters as described [here](https://flask-ldap3-login.readthedocs.io/en/latest/configuration.html).

Some extra parameters are available:

| Parameter | Default value | Notes |
|-----------|---------------|-------|
| `LDAP_KERBEROS` | `False` | |
| `LDAP_KERBEROS_KEYTAB` | `None` | |
| `LDAP_KERBEROS_SERVICE_NAME` | 'HTTP' | |
| `LDAP_KERBEROS_SERVICE_HOSTNAME` | `socket.getfqdn()` ||
| `LDAP_KERBEROS_SPNEGO` | `False` ||
| `LDAP_USER_SPNEGO_ATTR` | `'uid'` ||

## Testing configuration

`udata-ldap` provides two commands to help with the configuration:

- `udata ldap config` will display the LDAP configuration seen by `udata`
- `udata ldap check` will allow to quickly test your configuration.

## Testing localy with docker

An example `docker-compose.yml` is provided to test localy wiht a freeipa server.

To use it, you need to copy the file `ipa-server-install-options.example` to `ipa-server-install-options` and edit it with your own parameters.

**ex:**

```
--unattended
--realm=DATA.XPS
--domain=data.xps
--ds-password=password
--admin-password=password
```
