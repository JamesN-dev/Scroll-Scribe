# Middleware

This document explains all middleware components that come with Django. For information on how to use them and how to write your own middleware, see the [middleware usage guide](../../topics/http/middleware/).

## Available middleware

### Cache middleware

- **class** `UpdateCacheMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/cache.py#L61)]
- **class** `FetchFromCacheMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/cache.py#L133)]

Enable the site-wide cache. If these are enabled, each Django-powered page will be cached for as long as the `CACHE_MIDDLEWARE_SECONDS` setting defines. See the [cache documentation](../../topics/cache/).

### “Common” middleware

- **class** `CommonMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/common.py#L13)]

  - **response_redirect_class**: Defaults to `HttpResponsePermanentRedirect`. Subclass `CommonMiddleware` and override the attribute to customize the redirects issued by the middleware.

Adds a few conveniences for perfectionists:

- Forbids access to user agents in the `DISALLOWED_USER_AGENTS` setting, which should be a list of compiled regular expression objects.
- Performs URL rewriting based on the `APPEND_SLASH` and `PREPEND_WWW` settings.

  If `APPEND_SLASH` is `True` and the initial URL doesn’t end with a slash, and it is not found in the URLconf, then a new URL is formed by appending a slash at the end. If this new URL is found in the URLconf, then Django redirects the request to this new URL. Otherwise, the initial URL is processed as usual.

  For example, `foo.com/bar` will be redirected to `foo.com/bar/` if you don’t have a valid URL pattern for `foo.com/bar` but *do* have a valid pattern for `foo.com/bar/`.

  If `PREPEND_WWW` is `True`, URLs that lack a leading “www.” will be redirected to the same URL with a leading “www.” Both of these options are meant to normalize URLs. The philosophy is that each URL should exist in one, and only one, place. Technically a URL `foo.com/bar` is distinct from `foo.com/bar/` – a search-engine indexer would treat them as separate URLs – so it’s best practice to normalize URLs.

  If necessary, individual views may be excluded from the `APPEND_SLASH` behavior using the `no_append_slash()` decorator:

  ```python
  from django.views.decorators.common import no_append_slash

  @no_append_slash
  def sensitive_fbv(request, *args, **kwargs):
      """View to be excluded from APPEND_SLASH."""
      return HttpResponse()
  ```

- Sets the `Content-Length` header for non-streaming responses.

- **class** `BrokenLinkEmailsMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/common.py#L118)]

  - Sends broken link notification emails to `MANAGERS` (see [How to manage error reporting](../../howto/error-reporting/)).

### GZip middleware

- **class** `GZipMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/gzip.py#L9)]

  - **max_random_bytes**: Defaults to 100. Subclass `GZipMiddleware` and override the attribute to change the maximum number of random bytes that is included with compressed responses.

**Note**

Security researchers revealed that when compression techniques (including `GZipMiddleware`) are used on a website, the site may become exposed to a number of possible attacks.

To mitigate attacks, Django implements a technique called *Heal The Breach (HTB)*. It adds up to 100 bytes (see `max_random_bytes`) of random bytes to each response to make the attacks less effective.

For more details, see the [BREACH paper (PDF)](https://www.breachattack.com/resources/BREACH%20-%20SSL,%20gone%20in%2030%20seconds.pdf), [breachattack.com](https://www.breachattack.com/), and the [Heal The Breach (HTB) paper](https://ieeexplore.ieee.org/document/9754554).

The `django.middleware.gzip.GZipMiddleware` compresses content for browsers that understand GZip compression (all modern browsers).

This middleware should be placed before any other middleware that need to read or write the response body so that compression happens afterward.

It will NOT compress content if any of the following are true:

- The content body is less than 200 bytes long.
- The response has already set the `Content-Encoding` header.
- The request (the browser) hasn’t sent an `Accept-Encoding` header containing `gzip`.

If the response has an `ETag` header, the ETag is made weak to comply with [RFC 9110 Section 8.8.1](https://datatracker.ietf.org/doc/html/rfc9110.html#section-8.8.1).

You can apply GZip compression to individual views using the `gzip_page()` decorator.

### Conditional GET middleware

- **class** `ConditionalGetMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/http.py#L6)]

Handles conditional GET operations. If the response doesn’t have an `ETag` header, the middleware adds one if needed. If the response has an `ETag` or `Last-Modified` header, and the request has `If-None-Match` or `If-Modified-Since`, the response is replaced by an `HttpResponseNotModified`.

You can handle conditional GET operations with individual views using the `conditional_page()` decorator.

### Locale middleware

- **class** `LocaleMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/locale.py#L10)]

  - **response_redirect_class**: Defaults to `HttpResponseRedirect`. Subclass `LocaleMiddleware` and override the attribute to customize the redirects issued by the middleware.

Enables language selection based on data from the request. It customizes content for each user. See the [internationalization documentation](../../topics/i18n/translation/).

### Message middleware

- **class** `MessageMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/messages/middleware.py#L6)]

Enables cookie- and session-based message support. See the [messages documentation](../contrib/messages/).

### Security middleware

**Warning**

If your deployment situation allows, it’s usually a good idea to have your front-end web server perform the functionality provided by the `SecurityMiddleware`. That way, if there are requests that aren’t served by Django (such as static media or user-uploaded files), they will have the same protections as requests to your Django application.

- **class** `SecurityMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/security.py#L8)]

The `django.middleware.security.SecurityMiddleware` provides several security enhancements to the request/response cycle. Each one can be independently enabled or disabled with a setting.

- `SECURE_CONTENT_TYPE_NOSNIFF`
- `SECURE_CROSS_ORIGIN_OPENER_POLICY`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`
- `SECURE_HSTS_SECONDS`
- `SECURE_REDIRECT_EXEMPT`
- `SECURE_REFERRER_POLICY`
- `SECURE_SSL_HOST`
- `SECURE_SSL_REDIRECT`

#### HTTP Strict Transport Security

For sites that should only be accessed over HTTPS, you can instruct modern browsers to refuse to connect to your domain name via an insecure connection (for a given period of time) by setting the [“Strict-Transport-Security” header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security). This reduces your exposure to some SSL-stripping man-in-the-middle (MITM) attacks.

`SecurityMiddleware` will set this header for you on all HTTPS responses if you set the `SECURE_HSTS_SECONDS` setting to a non-zero integer value.

When enabling HSTS, it’s a good idea to first use a small value for testing, for example, `SECURE_HSTS_SECONDS = 3600` for one hour. Each time a web browser sees the HSTS header from your site, it will refuse to communicate non-securely (using HTTP) with your domain for the given period of time. Once you confirm that all assets are served securely on your site (i.e. HSTS didn’t break anything), it’s a good idea to increase this value so that infrequent visitors will be protected (31536000 seconds, i.e. 1 year, is common).

Additionally, if you set the `SECURE_HSTS_INCLUDE_SUBDOMAINS` setting to `True`, `SecurityMiddleware` will add the `includeSubDomains` directive to the `Strict-Transport-Security` header. This is recommended (assuming all subdomains are served exclusively using HTTPS), otherwise your site may still be vulnerable via an insecure connection to a subdomain.

If you wish to submit your site to the [browser preload list](https://hstspreload.org/), set the `SECURE_HSTS_PRELOAD` setting to `True`. That appends the `preload` directive to the `Strict-Transport-Security` header.

**Warning**

The HSTS policy applies to your entire domain, not just the URL of the response that you set the header on. Therefore, you should only use it if your entire domain is served via HTTPS only.

Browsers properly respecting the HSTS header will refuse to allow users to bypass warnings and connect to a site with an expired, self-signed, or otherwise invalid SSL certificate. If you use HSTS, make sure your certificates are in good shape and stay that way!

**Note**

If you are deployed behind a load-balancer or reverse-proxy server, and the `Strict-Transport-Security` header is not being added to your responses, it may be because Django doesn’t realize that it’s on a secure connection; you may need to set the `SECURE_PROXY_SSL_HEADER` setting.

#### Referrer Policy

Browsers use [the Referer header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referer) as a way to send information to a site about how users got there. When a user clicks a link, the browser will send the full URL of the linking page as the referrer. While this can be useful for some purposes – like figuring out who’s linking to your site – it also can cause privacy concerns by informing one site that a user was visiting another site.

Some browsers have the ability to accept hints about whether they should send the HTTP `Referer` header when a user clicks a link; this hint is provided via [the Referrer-Policy header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy). This header can suggest any of three behaviors to browsers:

- Full URL: send the entire URL in the `Referer` header. For example, if the user is visiting `https://example.com/page.html`, the `Referer` header would contain `"https://example.com/page.html"`.
- Origin only: send only the “origin” in the referrer. The origin consists of the scheme, host and (optionally) port number. For example, if the user is visiting `https://example.com/page.html`, the origin would be `https://example.com/`.
- No referrer: do not send a `Referer` header at all.

There are two types of conditions this header can tell a browser to watch out for:

- Same-origin versus cross-origin: a link from `https://example.com/1.html` to `https://example.com/2.html` is same-origin. A link from `https://example.com/page.html` to `https://not.example.com/page.html` is cross-origin.
- Protocol downgrade: a downgrade occurs if the page containing the link is served via HTTPS, but the page being linked to is not served via HTTPS.

**Warning**

When your site is served via HTTPS, [Django’s CSRF protection system](../csrf/#how-csrf-works) requires the `Referer` header to be present, so completely disabling the `Referer` header will interfere with CSRF protection. To gain most of the benefits of disabling `Referer` headers while also keeping CSRF protection, consider enabling only same-origin referrers.

`SecurityMiddleware` can set the `Referrer-Policy` header for you, based on the `SECURE_REFERRER_POLICY` setting (note spelling: browsers send a `Referer` header when a user clicks a link, but the header instructing a browser whether to do so is spelled `Referrer-Policy`). The valid values for this setting are:

- `no-referrer`: Instructs the browser to send no referrer for links clicked on this site.
- `no-referrer-when-downgrade`: Instructs the browser to send a full URL as the referrer, but only when no protocol downgrade occurs.
- `origin`: Instructs the browser to send only the origin, not the full URL, as the referrer.
- `origin-when-cross-origin`: Instructs the browser to send the full URL as the referrer for same-origin links, and only the origin for cross-origin links.
- `same-origin`: Instructs the browser to send a full URL, but only for same-origin links. No referrer will be sent for cross-origin links.
- `strict-origin`: Instructs the browser to send only the origin, not the full URL, and to send no referrer when a protocol downgrade occurs.
- `strict-origin-when-cross-origin`: Instructs the browser to send the full URL when the link is same-origin and no protocol downgrade occurs; send only the origin when the link is cross-origin and no protocol downgrade occurs; and no referrer when a protocol downgrade occurs.
- `unsafe-url`: Instructs the browser to always send the full URL as the referrer.

**Unknown Policy Values**

Where a policy value is [unknown](https://w3c.github.io/webappsec-referrer-policy/#unknown-policy-values) by a user agent, it is possible to specify multiple policy values to provide a fallback. The last specified value that is understood takes precedence. To support this, an iterable or comma-separated string can be used with `SECURE_REFERRER_POLICY`.

#### Cross-Origin Opener Policy

Some browsers have the ability to isolate top-level windows from other documents by putting them in a separate browsing context group based on the value of the [Cross-Origin Opener Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy) (COOP) header. If a document that is isolated in this way opens a cross-origin popup window, the popup’s `window.opener` property will be `null`. Isolating windows using COOP is a defense-in-depth protection against cross-origin attacks, especially those like Spectre which allowed exfiltration of data loaded into a shared browsing context.

`SecurityMiddleware` can set the `Cross-Origin-Opener-Policy` header for you, based on the `SECURE_CROSS_ORIGIN_OPENER_POLICY` setting. The valid values for this setting are:

- `same-origin`: Isolates the browsing context exclusively to same-origin documents. Cross-origin documents are not loaded in the same browsing context. This is the default and most secure option.
- `same-origin-allow-popups`: Isolates the browsing context to same-origin documents or those which either don’t set COOP or which opt out of isolation by setting a COOP of `unsafe-none`.
- `unsafe-none`: Allows the document to be added to its opener’s browsing context group unless the opener itself has a COOP of `same-origin` or `same-origin-allow-popups`.

#### `X-Content-Type-Options: nosniff`

Some browsers will try to guess the content types of the assets that they fetch, overriding the `Content-Type` header. While this can help display sites with improperly configured servers, it can also pose a security risk.

If your site serves user-uploaded files, a malicious user could upload a specially-crafted file that would be interpreted as HTML or JavaScript by the browser when you expected it to be something harmless.

To prevent the browser from guessing the content type and force it to always use the type provided in the `Content-Type` header, you can pass the [X-Content-Type-Options: nosniff](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options) header. `SecurityMiddleware` will do this for all responses if the `SECURE_CONTENT_TYPE_NOSNIFF` setting is `True`.

Note that in most deployment situations where Django isn’t involved in serving user-uploaded files, this setting won’t help you. For example, if your `MEDIA_URL` is served directly by your front-end web server (nginx, Apache, etc.) then you’d want to set this header there. On the other hand, if you are using Django to do something like require authorization in order to download files and you cannot set the header using your web server, this setting will be useful.

#### SSL Redirect

If your site offers both HTTP and HTTPS connections, most users will end up with an unsecured connection by default. For best security, you should redirect all HTTP connections to HTTPS.

If you set the `SECURE_SSL_REDIRECT` setting to True, `SecurityMiddleware` will permanently (HTTP 301) redirect all HTTP connections to HTTPS.

**Note**

For performance reasons, it’s preferable to do these redirects outside of Django, in a front-end load balancer or reverse-proxy server such as [nginx](https://nginx.org/). `SECURE_SSL_REDIRECT` is intended for the deployment situations where this isn’t an option.

If the `SECURE_SSL_HOST` setting has a value, all redirects will be sent to that host instead of the originally-requested host.

If there are a few pages on your site that should be available over HTTP, and not redirected to HTTPS, you can list regular expressions to match those URLs in the `SECURE_REDIRECT_EXEMPT` setting.

**Note**

If you are deployed behind a load-balancer or reverse-proxy server and Django can’t seem to tell when a request actually is already secure, you may need to set the `SECURE_PROXY_SSL_HEADER` setting.

### Session middleware

- **class** `SessionMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/sessions/middleware.py#L12)]

Enables session support. See the [session documentation](../../topics/http/sessions/).

### Site middleware

- **class** `CurrentSiteMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/sites/middleware.py#L6)]

Adds the `site` attribute representing the current site to every incoming `HttpRequest` object. See the [sites documentation](../contrib/sites/#site-middleware).

### Authentication middleware

- **class** `AuthenticationMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/auth/middleware.py#L29)]

Adds the `user` attribute, representing the currently-logged-in user, to every incoming `HttpRequest` object. See [Authentication in web requests](../../topics/auth/default/#auth-web-requests).

- **class** `LoginRequiredMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/auth/middleware.py#L43)]

  - **redirect_field_name**: Defaults to `"next"`.
  - **get_login_url()**: Returns the URL that unauthenticated requests will be redirected to. This result is either the `login_url` set on the `login_required()` decorator (if not `None`), or `settings.LOGIN_URL`.
  - **get_redirect_field_name()**: Returns the name of the query parameter that contains the URL the user should be redirected to after a successful login. This result is either the `redirect_field_name` set on the `login_required()` decorator (if not `None`), or `redirect_field_name`. If `None` is returned, a query parameter won’t be added.

**New in Django 5.1.**

Redirects all unauthenticated requests to a login page, except for views excluded with `login_not_required()`. The login page defaults to `settings.LOGIN_URL`, but can be customized.

Enable this middleware by adding it to the `MIDDLEWARE` setting **after** `AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    "...",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "...",
]
```

Make a view public, allowing unauthenticated requests, with `login_not_required()`. For example:

```python
from django.contrib.auth.decorators import login_not_required

@login_not_required
def contact_us(request):
    ...
```

Customize the login URL or field name for authenticated views with the `login_required()` decorator to set `login_url` or `redirect_field_name` respectively. For example:

```python
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View

@login_required(login_url="/books/login/", redirect_field_name="redirect_to")
def book_dashboard(request):
    ...

@method_decorator(
    login_required(login_url="/books/login/", redirect_field_name="redirect_to"),
    name="dispatch",
)
class BookMetrics(View):
    pass
```

**Ensure that your login view does not require a login.**

To prevent infinite redirects, ensure you have [enabled unauthenticated requests](../../topics/auth/default/#disable-login-required-middleware-for-views) to your login view.

- **class** `RemoteUserMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/auth/middleware.py#L93)]

Middleware for utilizing web server provided authentication. See [How to authenticate using REMOTE_USER](../../howto/auth-remote-user/) for usage details.

- **class** `PersistentRemoteUserMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/contrib/auth/middleware.py#L260)]

Middleware for utilizing web server provided authentication when enabled only on the login page. See [Using REMOTE_USER on login pages only](../../howto/auth-remote-user/#persistent-remote-user-middleware-howto) for usage details.

### CSRF protection middleware

- **class** `CsrfViewMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/csrf.py#L165)]

Adds protection against Cross Site Request Forgeries by adding hidden form fields to POST forms and checking requests for the correct value. See the [Cross Site Request Forgery protection documentation](../csrf/).

You can add Cross Site Request Forgery protection to individual views using the `csrf_protect()` decorator.

### `X-Frame-Options` middleware

- **class** `XFrameOptionsMiddleware` [[source](https://github.com/django/django/blob/stable/5.2.x/django/middleware/clickjacking.py#L12)]

Simple [clickjacking protection via the X-Frame-Options header](../clickjacking/).

## Middleware ordering

Here are some hints about the ordering of various Django middleware classes:

1. **SecurityMiddleware**

   It should go near the top of the list if you’re going to turn on the SSL redirect as that avoids running through a bunch of other unnecessary middleware.

2. **UpdateCacheMiddleware**

   Before those that modify the `Vary` header (`SessionMiddleware`, `GZipMiddleware`, `LocaleMiddleware`).

3. **GZipMiddleware**

   Before any middleware that may change or use the response body.

   After `UpdateCacheMiddleware`: Modifies `Vary` header.

4. **SessionMiddleware**

   Before any middleware that may raise an exception to trigger an error view (such as `PermissionDenied`) if you’re using `CSRF_USE_SESSIONS`.

   After `UpdateCacheMiddleware`: Modifies `Vary` header.

5. **ConditionalGetMiddleware**

   Before any middleware that may change the response (it sets the `ETag` header).

   After `GZipMiddleware` so it won’t calculate an `ETag` header on gzipped contents.

6. **LocaleMiddleware**

   One of the topmost, after `SessionMiddleware` (uses session data) and `UpdateCacheMiddleware` (modifies `Vary` header).

7. **CommonMiddleware**

   Before any middleware that may change the response (it sets the `Content-Length` header). A middleware that appears before `CommonMiddleware` and changes the response must reset `Content-Length`.

   Close to the top: it redirects when `APPEND_SLASH` or `PREPEND_WWW` are set to `True`.

   After `SessionMiddleware` if you’re using `CSRF_USE_SESSIONS`.

8. **CsrfViewMiddleware**

   Before any view middleware that assumes that CSRF attacks have been dealt with.

   Before `RemoteUserMiddleware`, or any other authentication middleware that may perform a login, and hence rotate the CSRF token, before calling down the middleware chain.

   After `SessionMiddleware` if you’re using `CSRF_USE_SESSIONS`.

9. **AuthenticationMiddleware**

   After `SessionMiddleware`: uses session storage.

10. **LoginRequiredMiddleware**

    **New in Django 5.1.**

    After `AuthenticationMiddleware`: uses user object.

11. **MessageMiddleware**

    After `SessionMiddleware`: can use session-based storage.

12. **FetchFromCacheMiddleware**

    After any middleware that modifies the `Vary` header: that header is used to pick a value for the cache hash-key.

13. **FlatpageFallbackMiddleware**

    Should be near the bottom as it’s a last-resort type of middleware.

14. **RedirectFallbackMiddleware**

    Should be near the bottom as it’s a last-resort type of middleware.