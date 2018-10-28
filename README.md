# udata-ldap

LDAP authentification for udata with optionnal Kerberos suppport.

## Requirements

To use LDAP only authentication, you only need the `udata-ldap` extension.

To use [`SASL`](https://en.wikipedia.org/wiki/Simple_Authentication_and_Security_Layer) and [`SPNEGO`](https://en.wikipedia.org/wiki/SPNEGO), you need a functional kerberos client environment.

On debian, you can install the requirements using:

```bash
apt-get install krb5-config krb5-user libkrb5-dev
```

You need to configure your domain in `/etc/krb5.conf`.
Here's a sample configuration for `DOMAIN.ORG`:

```ini
[libdefaults]
    default_realm = DOMAIN.ORG

[realms]
    DATA.XPS = {
        #admin_server = ipa.data.xps
        # use "kdc = ..." if realm admins haven't put SRV records into DNS
        kdc = kdc.domain.org
        admin_server = kdc.domain.org:749
        default_domain = domain.org
        dns_lookup_realm = false
        dns_lookup_kdc = false
        rdns = false
    }

[domain_realm]
    domain.org = DOMAIN.ORG
    .domain.org = DOMAIN.ORG
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
| `LDAP_DEBUG` | `False` | Enable verbose/debug logging |
| `LDAP_KERBEROS_KEYTAB` | `None` | Path to an optionnal Kerberos keytab for this service |
| `LDAP_KERBEROS_SERVICE_NAME` | `'HTTP'` | The service principal as configured in the keytab |
| `LDAP_KERBEROS_SERVICE_HOSTNAME` | `socket.getfqdn()` | The service hostname (ie. `data.domain.com`) |
| `LDAP_KERBEROS_SPNEGO` | `False` | Whether or not to enable passwordless authentication with SPNEGO |
| `LDAP_REMOTE_USER_ATTR` | `'uid'` | The ldap attribute extracted from SPNEGO handshake to match the user |
| `LDAP_USER_FIRST_NAME_ATTR` | `'givenName'` | The ldap attribute to extract the first name from |
| `LDAP_USER_LAST_NAME_ATTR` | `'sn'` | The ldap attribute to extract the last name from |

## Testing configuration

`udata-ldap` provides two commands to help with the configuration:

- `udata ldap config` will display the LDAP configuration seen by `udata`
- `udata ldap check` will allow to quickly test your LDAP configuration.
- `udata ldap krbcheck` will allow to quickly test your Kerberos configuration.

## Testing localy with docker

An example `docker-compose.yml` is provided to test localy wiht a freeipa server.

To use it, you need to copy the file `ipa-server-install-options.example` to `ipa-server-install-options` and edit it with your own parameters.

**ex:**

```
--unattended
--realm=DOMAIN.ORG
--domain=DOMAIN.ORG
--ds-password=password
--admin-password=password
```
