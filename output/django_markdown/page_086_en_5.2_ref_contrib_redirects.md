# The Redirects App

Django comes with an optional redirects application. It lets you store redirects in a database and handles the redirecting for you. It uses the HTTP response status code `301 Moved Permanently` by default.

## Installation

To install the redirects app, follow these steps:

1. Ensure that the `django.contrib.sites` framework [is installed](https://docs.djangoproject.com/en/5.2/sites/#enabling-the-sites-framework).
2. Add `'django.contrib.redirects'` to your [`INSTALLED_APPS`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-INSTALLED_APPS) setting.
3. Add `'django.contrib.redirects.middleware.RedirectFallbackMiddleware'` to your [`MIDDLEWARE`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-MIDDLEWARE) setting.
4. Run the command [`manage.py migrate`](https://docs.djangoproject.com/en/5.2/django-admin/#django-admin-migrate).

## How It Works

`manage.py migrate` creates a `django_redirect` table in your database. This is a lookup table with `site_id`, `old_path` and `new_path` fields.

The [`RedirectFallbackMiddleware`](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/#django.contrib.redirects.middleware.RedirectFallbackMiddleware) does all of the work. Each time any Django application raises a 404 error, this middleware checks the redirects database for the requested URL as a last resort. Specifically, it checks for a redirect with the given `old_path` with a site ID that corresponds to the [`SITE_ID`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-SITE_ID) setting.

*   If it finds a match, and `new_path` is not empty, it redirects to `new_path` using a 301 (“Moved Permanently”) redirect. You can subclass [`RedirectFallbackMiddleware`](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/#django.contrib.redirects.middleware.RedirectFallbackMiddleware) and set [`response_redirect_class`](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/#django.contrib.redirects.middleware.RedirectFallbackMiddleware.response_redirect_class) to [`django.http.HttpResponseRedirect`](https://docs.djangoproject.com/en/5.2/request-response/#django.http.HttpResponseRedirect) to use a `302 Moved Temporarily` redirect instead.
*   If it finds a match, and `new_path` is empty, it sends a 410 (“Gone”) HTTP header and empty (content-less) response.
*   If it doesn’t find a match, the request continues to be processed as usual.

The middleware only gets activated for 404s – not for 500s or responses of any other status code.

Note that the order of [`MIDDLEWARE`](https://docs.djangoproject.com/en/5.2/settings/#std-setting-MIDDLEWARE) matters. Generally, you can put [`RedirectFallbackMiddleware`](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/#django.contrib.redirects.middleware.RedirectFallbackMiddleware) at the end of the list, because it’s a last resort.

For more on middleware, read the [middleware docs](https://docs.djangoproject.com/en/5.2/topics/http/middleware/).

## How To Add, Change And Delete Redirects

### Via The Admin Interface

If you’ve activated the automatic Django admin interface, you should see a “Redirects” section on the admin index page. Edit redirects as you edit any other object in the system.

### Via The Python Api

*class* `models.Redirect`

Redirects are represented by a standard [Django model](https://docs.djangoproject.com/en/5.2/topics/db/models/), which lives in [django/contrib/redirects/models.py](https://github.com/django/django/blob/main/django/contrib/redirects/models.py). You can access redirect objects via the [Django database API](https://docs.djangoproject.com/en/5.2/topics/db/queries/). For example:

```
>>> from django.conf import settings
>>> from django.contrib.redirects.models import Redirect
>>> # Add a new redirect.
>>> redirect = Redirect.objects.create(
...     site_id=1,
...     old_path="/contact-us/",
...     new_path="/contact/",
... )
>>> # Change a redirect.
>>> redirect.new_path = "/contact-details/"
>>> redirect.save()
>>> redirect
<Redirect: /contact-us/ ---> /contact-details/>
>>> # Delete a redirect.
>>> Redirect.objects.filter(site_id=1, old_path="/contact-us/").delete()
(1, {'redirects.Redirect': 1})
```

## Middleware

*class* `middleware.RedirectFallbackMiddleware`

You can change the [`HttpResponse`](https://docs.djangoproject.com/en/5.2/request-response/#django.http.HttpResponse) classes used by the middleware by creating a subclass of [`RedirectFallbackMiddleware`](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/#django.contrib.redirects.middleware.RedirectFallbackMiddleware) and overriding `response_gone_class` and/or `response_redirect_class`.

`response_gone_class`

The [`HttpResponse`](https://docs.djangoproject.com/en/5.2/request-response/#django.http.HttpResponse) class used when a [`Redirect`](https://docs.djangoproject.com/en/5.2/ref/contrib/redirects/#django.contrib.redirects.models.Redirect) is not found for the requested path or has a blank `new_path` value.

Defaults to [`HttpResponseGone`](https://docs.djangoproject.com/en/5.2/request-response/#django.http.HttpResponseGone).

`response_redirect_class`

The [`HttpResponse`](https://docs.djangoproject.com/en/5.2/request-response/#django.http.HttpResponse) class that handles the redirect.

Defaults to [`HttpResponsePermanentRedirect`](https://docs.djangoproject.com/en/5.2/request-response/#django.http.HttpResponsePermanentRedirect).