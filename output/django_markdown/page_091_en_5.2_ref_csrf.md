# Cross Site Request Forgery Protection

The CSRF middleware and template tag provides easy-to-use protection against [Cross Site Request Forgeries](https://owasp.org/www-community/attacks/csrf#overview). This type of attack occurs when a malicious website contains a link, a form button or some JavaScript that is intended to perform some action on your website, using the credentials of a logged-in user who visits the malicious site in their browser. A related type of attack, ‘login CSRF’, where an attacking site tricks a user’s browser into logging into a site with someone else’s credentials, is also covered.

The first defense against CSRF attacks is to ensure that GET requests (and other ‘safe’ methods, as defined by [RFC 9110 Section 9.2.1](https://datatracker.ietf.org/doc/html/rfc9110.html#section-9.2.1)) are side effect free. Requests via ‘unsafe’ methods, such as POST, PUT, and DELETE, can then be protected by the steps outlined in [How To Use Django’s CSRF Protection](../../howto/csrf/#using-csrf).

## How It Works

The CSRF protection is based on the following things:

1.  A CSRF cookie that is a random secret value, which other sites will not have access to.

    `CsrfViewMiddleware` sends this cookie with the response whenever `django.middleware.csrf.get_token()` is called. It can also send it in other cases. For security reasons, the value of the secret is changed each time a user logs in.

2.  A hidden form field with the name ‘csrfmiddlewaretoken’, present in all outgoing POST forms.

    In order to protect against [BREACH](https://www.breachattack.com/) attacks, the value of this field is not simply the secret. It is scrambled differently with each response using a mask. The mask is generated randomly on every call to `get_token()`, so the form field value is different each time.

    This part is done by the [`csrf_token`](../templates/builtins/#std-templatetag-csrf_token) template tag.

3.  For all incoming requests that are not using HTTP GET, HEAD, OPTIONS or TRACE, a CSRF cookie must be present, and the ‘csrfmiddlewaretoken’ field must be present and correct. If it isn’t, the user will get a 403 error.

    When validating the ‘csrfmiddlewaretoken’ field value, only the secret, not the full token, is compared with the secret in the cookie value. This allows the use of ever-changing tokens. While each request may use its own token, the secret remains common to all.

    This check is done by `CsrfViewMiddleware`.

4.  `CsrfViewMiddleware` verifies the [Origin header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Origin), if provided by the browser, against the current host and the [`CSRF_TRUSTED_ORIGINS`](../settings/#std-setting-CSRF_TRUSTED_ORIGINS) setting. This provides protection against cross-subdomain attacks.

5.  In addition, for HTTPS requests, if the `Origin` header isn’t provided, `CsrfViewMiddleware` performs strict referer checking. This means that even if a subdomain can set or modify cookies on your domain, it can’t force a user to post to your application since that request won’t come from your own exact domain.

    This also addresses a man-in-the-middle attack that’s possible under HTTPS when using a session independent secret, due to the fact that HTTP `Set-Cookie` headers are (unfortunately) accepted by clients even when they are talking to a site under HTTPS. (Referer checking is not done for HTTP requests because the presence of the `Referer` header isn’t reliable enough under HTTP.)

    If the [`CSRF_COOKIE_DOMAIN`](../settings/#std-setting-CSRF_COOKIE_DOMAIN) setting is set, the referer is compared against it. You can allow cross-subdomain requests by including a leading dot. For example, `CSRF_COOKIE_DOMAIN = '.example.com'` will allow POST requests from `www.example.com` and `api.example.com`. If the setting is not set, then the referer must match the HTTP `Host` header.

    Expanding the accepted referers beyond the current host or cookie domain can be done with the [`CSRF_TRUSTED_ORIGINS`](../settings/#std-setting-CSRF_TRUSTED_ORIGINS) setting.

This ensures that only forms that have originated from trusted domains can be used to POST data back.

It deliberately ignores GET requests (and other requests that are defined as ‘safe’ by [RFC 9110 Section 9.2.1](https://datatracker.ietf.org/doc/html/rfc9110.html#section-9.2.1)). These requests ought never to have any potentially dangerous side effects, and so a CSRF attack with a GET request ought to be harmless. [RFC 9110 Section 9.2.1](https://datatracker.ietf.org/doc/html/rfc9110.html#section-9.2.1) defines POST, PUT, and DELETE as ‘unsafe’, and all other methods are also assumed to be unsafe, for maximum protection.

The CSRF protection cannot protect against man-in-the-middle attacks, so use [HTTPS](../../topics/security/#security-recommendation-ssl) with [HTTP Strict Transport Security](../middleware/#http-strict-transport-security). It also assumes [validation of the HOST header](../../topics/security/#host-headers-virtual-hosting) and that there aren’t any [cross-site scripting vulnerabilities](../../topics/security/#cross-site-scripting) on your site (because XSS vulnerabilities already let an attacker do anything a CSRF vulnerability allows and much worse).

Removing the `Referer` header

To avoid disclosing the referrer URL to third-party sites, you might want to [disable the referer](https://www.w3.org/TR/referrer-policy/#referrer-policy-delivery) on your site’s `` tags. For example, you might use the `` tag or include the `Referrer-Policy: no-referrer` header. Due to the CSRF protection’s strict referer checking on HTTPS requests, those techniques cause a CSRF failure on requests with ‘unsafe’ methods. Instead, use alternatives like `` for links to third-party sites.

## Limitations

Subdomains within a site will be able to set cookies on the client for the whole domain. By setting the cookie and using a corresponding token, subdomains will be able to circumvent the CSRF protection. The only way to avoid this is to ensure that subdomains are controlled by trusted users (or, are at least unable to set cookies). Note that even without CSRF, there are other vulnerabilities, such as session fixation, that make giving subdomains to untrusted parties a bad idea, and these vulnerabilities cannot easily be fixed with current browsers.

## Utilities

The examples below assume you are using function-based views. If you are working with class-based views, you can refer to [Decorating Class-Based Views](../../topics/class-based-views/intro/#id1).

`csrf_exempt(view)`

This decorator marks a view as being exempt from the protection ensured by the middleware. Example:

```python
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def my_view(request):
    return HttpResponse("Hello world")
```

`csrf_protect(view)`

Decorator that provides the protection of [`CsrfViewMiddleware`](../middleware/#django.middleware.csrf.CsrfViewMiddleware) to a view.

Usage:

```python
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def my_view(request):
    c = {}
    # ...
    return render(request, "a_template.html", c)
```

`requires_csrf_token(view)`

Normally the [`csrf_token`](../templates/builtins/#std-templatetag-csrf_token) template tag will not work if `CsrfViewMiddleware.process_view` or an equivalent like `csrf_protect` has not run. The view decorator `requires_csrf_token` can be used to ensure the template tag does work. This decorator works similarly to `csrf_protect`, but never rejects an incoming request.

Example:

```python
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token

@requires_csrf_token
def my_view(request):
    c = {}
    # ...
    return render(request, "a_template.html", c)
```

`ensure_csrf_cookie(view)`

This decorator forces a view to send the CSRF cookie.

## Settings

A number of settings can be used to control Django’s CSRF behavior:

*   [`CSRF_COOKIE_AGE`](../settings/#std-setting-CSRF_COOKIE_AGE)
*   [`CSRF_COOKIE_DOMAIN`](../settings/#std-setting-CSRF_COOKIE_DOMAIN)
*   [`CSRF_COOKIE_HTTPONLY`](../settings/#std-setting-CSRF_COOKIE_HTTPONLY)
*   [`CSRF_COOKIE_NAME`](../settings/#std-setting-CSRF_COOKIE_NAME)
*   [`CSRF_COOKIE_PATH`](../settings/#std-setting-CSRF_COOKIE_PATH)
*   [`CSRF_COOKIE_SAMESITE`](../settings/#std-setting-CSRF_COOKIE_SAMESITE)
*   [`CSRF_COOKIE_SECURE`](../settings/#std-setting-CSRF_COOKIE_SECURE)
*   [`CSRF_FAILURE_VIEW`](../settings/#std-setting-CSRF_FAILURE_VIEW)
*   [`CSRF_HEADER_NAME`](../settings/#std-setting-CSRF_HEADER_NAME)
*   [`CSRF_TRUSTED_ORIGINS`](../settings/#std-setting-CSRF_TRUSTED_ORIGINS)
*   [`CSRF_USE_SESSIONS`](../settings/#std-setting-CSRF_USE_SESSIONS)

## Frequently Asked Questions

### Is Posting An Arbitrary CSRF Token Pair (Cookie And Post Data) A Vulnerability?

No, this is by design. Without a man-in-the-middle attack, there is no way for an attacker to send a CSRF token cookie to a victim’s browser, so a successful attack would need to obtain the victim’s browser’s cookie via XSS or similar, in which case an attacker usually doesn’t need CSRF attacks.

Some security audit tools flag this as a problem but as mentioned before, an attacker cannot steal a user’s browser’s CSRF cookie. “Stealing” or modifying *your own* token using Firebug, Chrome dev tools, etc. isn’t a vulnerability.

### Is It A Problem That Django’s CSRF Protection Isn’t Linked To A Session By Default?

No, this is by design. Not linking CSRF protection to a session allows using the protection on sites such as a *pastebin* that allow submissions from anonymous users which don’t have a session.

If you wish to store the CSRF token in the user’s session, use the [`CSRF_USE_SESSIONS`](../settings/#std-setting-CSRF_USE_SESSIONS) setting.

### Why Might A User Encounter A CSRF Validation Failure After Logging In?

For security reasons, CSRF tokens are rotated each time a user logs in. Any page with a form generated before a login will have an old, invalid CSRF token and need to be reloaded. This might happen if a user uses the back button after a login or if they log in a different browser tab.