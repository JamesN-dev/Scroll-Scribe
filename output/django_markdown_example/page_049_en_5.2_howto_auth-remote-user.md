# How to authenticate using `REMOTE_USER`

This document describes how to make use of external authentication sources (where the web server sets the `REMOTE_USER` environment variable) in your Django applications. This type of authentication solution is typically seen on intranet sites, with single sign-on solutions such as IIS and Integrated Windows Authentication or Apache and [mod_authnz_ldap](https://httpd.apache.org/docs/current/mod/mod_authnz_ldap.html), [CAS](https://www.apereo.org/projects/cas), [WebAuth](https://uit.stanford.edu/service/authentication), [mod_auth_sspi](https://sourceforge.net/projects/mod-auth-sspi), etc.

When the web server takes care of authentication it typically sets the `REMOTE_USER` environment variable for use in the underlying application. In Django, `REMOTE_USER` is made available in the `request.META` attribute. Django can be configured to make use of the `REMOTE_USER` value using the `RemoteUserMiddleware` or `PersistentRemoteUserMiddleware`, and `RemoteUserBackend` classes found in `django.contrib.auth`.

## Configuration

First, you must add the `django.contrib.auth.middleware.RemoteUserMiddleware` to the `MIDDLEWARE` setting **after** the `django.contrib.auth.middleware.AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    "...",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    "...",
]
```

Next, you must replace the `ModelBackend` with `RemoteUserBackend` in the `AUTHENTICATION_BACKENDS` setting:

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.RemoteUserBackend",
]
```

With this setup, `RemoteUserMiddleware` will detect the username in `request.META['REMOTE_USER']` and will authenticate and auto-login that user using the `RemoteUserBackend`.

Be aware that this particular setup disables authentication with the default `ModelBackend`. This means that if the `REMOTE_USER` value is not set then the user is unable to log in, even using Django's admin interface. Adding `'django.contrib.auth.backends.ModelBackend'` to the `AUTHENTICATION_BACKENDS` list will use `ModelBackend` as a fallback if `REMOTE_USER` is absent, which will solve these issues.

> **Note**
> 
> Since the `RemoteUserBackend` inherits from `ModelBackend`, you will still have all of the same permissions checking that is implemented in `ModelBackend`.
> 
> Users with `is_active=False` won't be allowed to authenticate. Use `AllowAllUsersRemoteUserBackend` if you want to allow them to.

If your authentication mechanism uses a custom HTTP header and not `REMOTE_USER`, you can subclass `RemoteUserMiddleware` and set the `header` attribute to the desired `request.META` key. For example:

```python
# mysite/middleware.py
from django.contrib.auth.middleware import RemoteUserMiddleware

class CustomHeaderRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_AUTHUSER"
```

This custom middleware is then used in the `MIDDLEWARE` setting instead of `django.contrib.auth.middleware.RemoteUserMiddleware`:

```python
MIDDLEWARE = [
    "...",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "mysite.middleware.CustomHeaderRemoteUserMiddleware",
    "...",
]
```

> **Warning**
> 
> Be very careful if using a `RemoteUserMiddleware` subclass with a custom HTTP header. You must be sure that your front-end web server always sets or strips that header based on the appropriate authentication checks, never permitting an end-user to submit a fake (or "spoofed") header value.

If you need more control, you can create your own authentication backend that inherits from `RemoteUserBackend` and override one or more of its attributes and methods.

## Using `REMOTE_USER` on login pages only

The `RemoteUserMiddleware` authentication middleware assumes that the HTTP request header `REMOTE_USER` is present with all authenticated requests. That might be expected and practical when Basic HTTP Auth with `htpasswd` or similar mechanisms are used, but with Negotiate (GSSAPI/Kerberos) or other resource intensive authentication methods, the authentication in the front-end HTTP server is usually only set up for one or a few login URLs.

`PersistentRemoteUserMiddleware` provides support for this use case. It will maintain the authenticated session until explicit logout by the user. The class can be used as a drop-in replacement of `RemoteUserMiddleware` in the documentation above.