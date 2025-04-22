# The Flatpages App

Django comes with an optional “flatpages” application. It lets you store “flat” HTML content in a database and handles the management for you via Django’s admin interface and a Python API.

A flatpage is an object with a URL, title and content. Use it for one-off, special-case pages, such as “About” or “Privacy Policy” pages, that you want to store in a database but for which you don’t want to develop a custom Django application.

A flatpage can use a custom template or a default, systemwide flatpage template. It can be associated with one, or multiple, sites.

The content field may optionally be left blank if you prefer to put your content in a custom template.

## Installation

To install the flatpages app, follow these steps:

1.  Install the [sites framework](https://docs.djangoproject.com/en/5.2/ref/contrib/sites/#module-django.contrib.sites) by adding `'django.contrib.sites'` to your [INSTALLED_APPS](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-INSTALLED_APPS) setting, if it’s not already in there.

    Also make sure you’ve correctly set [SITE_ID](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SITE_ID) to the ID of the site the settings file represents. This will usually be `1` (i.e. `SITE_ID = 1`), but if you’re using the sites framework to manage multiple sites, it could be the ID of a different site.
2.  Add `'django.contrib.flatpages'` to your [INSTALLED_APPS](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-INSTALLED_APPS) setting.

Then either:

1.  Add an entry in your URLconf. For example:

    ```python
    urlpatterns = [
        path("pages/", include("django.contrib.flatpages.urls")),
    ]
    ```

or:

1.  Add `'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'` to your [MIDDLEWARE](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-MIDDLEWARE) setting.
2.  Run the command [manage.py migrate](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-migrate).

## How It Works

`manage.py migrate` creates two tables in your database: `django_flatpage` and `django_flatpage_sites`. `django_flatpage` is a lookup table that maps a URL to a title and bunch of text content. `django_flatpage_sites` associates a flatpage with a site.

### Using The Urlconf

There are several ways to include the flat pages in your URLconf. You can dedicate a particular path to flat pages:

```python
urlpatterns = [
    path("pages/", include("django.contrib.flatpages.urls")),
]
```

You can also set it up as a “catchall” pattern. In this case, it is important to place the pattern at the end of the other urlpatterns:

```python
from django.contrib.flatpages import views

# Your other patterns here
urlpatterns += [
    re_path(r"^(?P<url>.*)/$", views.flatpage),
]
```

> Warning
>
> If you set [APPEND_SLASH](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-APPEND_SLASH) to `False`, you must remove the slash in the catchall pattern or flatpages without a trailing slash will not be matched.

Another common setup is to use flat pages for a limited set of known pages and to hard code their URLs in the [URLconf](https://docs.djangoproject.com/en/5.2/topics/http/urls/):

```python
from django.contrib.flatpages import views

urlpatterns += [
    path("about-us/", views.flatpage, kwargs={"url": "/about-us/"}, name="about"),
    path("license/", views.flatpage, kwargs={"url": "/license/"}, name="license"),
]
```

The `kwargs` argument sets the `url` value used for the `FlatPage` model lookup in the flatpage view.

The `name` argument allows the URL to be reversed in templates, for example using the [url](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#std-templatetag-url) template tag.

### Using The Middleware

The [FlatpageFallbackMiddleware](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#django.contrib.flatpages.middleware.FlatpageFallbackMiddleware) can do all of the work.

::: django.contrib.flatpages.middleware.FlatpageFallbackMiddleware

:::

> Flatpages will not apply view middleware
>
> Because the `FlatpageFallbackMiddleware` is applied only after URL resolution has failed and produced a 404, the response it returns will not apply any [view middleware](https://docs.djangoproject.com/en/5.2/topics/http/middleware/#view-middleware) methods. Only requests which are successfully routed to a view via normal URL resolution apply view middleware.

Note that the order of [MIDDLEWARE](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-MIDDLEWARE) matters. Generally, you can put [FlatpageFallbackMiddleware](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#django.contrib.flatpages.middleware.FlatpageFallbackMiddleware) at the end of the list. This means it will run first when processing the response, and ensures that any other response-processing middleware see the real flatpage response rather than the 404.

For more on middleware, read the [middleware docs](https://docs.djangoproject.com/en/5.2/topics/http/middleware/).

> Ensure that your 404 template works
>
> Note that the [FlatpageFallbackMiddleware](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#django.contrib.flatpages.middleware.FlatpageFallbackMiddleware) only steps in once another view has successfully produced a 404 response. If another view or middleware class attempts to produce a 404 but ends up raising an exception instead, the response will become an HTTP 500 (“Internal Server Error”) and the [FlatpageFallbackMiddleware](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#django.contrib.flatpages.middleware.FlatpageFallbackMiddleware) will not attempt to serve a flat page.

## How To Add, Change And Delete Flatpages

> Warning
>
> Permissions to add or edit flatpages should be restricted to trusted users. Flatpages are defined by raw HTML and are **not sanitized** by Django. As a consequence, a malicious flatpage can lead to various security vulnerabilities, including permission escalation.

### Via The Admin Interface

If you’ve activated the automatic Django admin interface, you should see a “Flatpages” section on the admin index page. Edit flatpages as you edit any other object in the system.

The `FlatPage` model has an `enable_comments` field that isn’t used by `contrib.flatpages`, but that could be useful for your project or third-party apps. It doesn’t appear in the admin interface, but you can add it by registering a custom `ModelAdmin` for `FlatPage`:

```python
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _

# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = [
        (None, {"fields": ["url", "title", "content", "sites"]}),
        (
            _("Advanced options"),
            {
                "classes": ["collapse"],
                "fields": [
                    "enable_comments",
                    "registration_required",
                    "template_name",
                ],
            },
        ),
    ]

# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
```

### Via The Python Api

::: django.contrib.flatpages.models.FlatPage

:::

> Check for duplicate flatpage URLs.
>
> If you add or modify flatpages via your own code, you will likely want to check for duplicate flatpage URLs within the same site. The flatpage form used in the admin performs this validation check, and can be imported from `django.contrib.flatpages.forms.FlatpageForm` and used in your own views.

## Flatpage Templates

By default, flatpages are rendered via the template `flatpages/default.html`, but you can override that for a particular flatpage: in the admin, a collapsed fieldset titled “Advanced options” (clicking will expand it) contains a field for specifying a template name. If you’re creating a flat page via the Python API you can set the template name as the field `template_name` on the `FlatPage` object.

Creating the `flatpages/default.html` template is your responsibility; in your template directory, create a `flatpages` directory containing a file `default.html`.

Flatpage templates are passed a single context variable, `flatpage`, which is the flatpage object.

Here’s a sample `flatpages/default.html` template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ flatpage.title }}</title>
</head>
<body>
    {{ flatpage.content }}
</body>
</html>
```

Since you’re already entering raw HTML into the admin page for a flatpage, both `flatpage.title` and `flatpage.content` are marked as **not** requiring [automatic HTML escaping](https://docs.djangoproject.com/en/5.2/ref/templates/language/#automatic-html-escaping) in the template.

## Getting A List Of Flatpage Objects In Your Templates

The flatpages app provides a template tag that allows you to iterate over all of the available flatpages on the [current site](https://docs.djangoproject.com/en/5.2/ref/contrib/sites/#hooking-into-current-site-from-views).

Like all custom template tags, you’ll need to [load its custom tag library](https://docs.djangoproject.com/en/5.2/ref/templates/language/#loading-custom-template-libraries) before you can use it. After loading the library, you can retrieve all current flatpages via the `get_flatpages` tag:

```html
{% load flatpages %}
{% get_flatpages as flatpages %}
<ul>
{% for page in flatpages %}
    <li><a href="{{ page.url }}">{{ page.title }}</a></li>
{% endfor %}
</ul>
```

### Displaying `Registration_Required` Flatpages

By default, the `get_flatpages` template tag will only show flatpages that are marked `registration_required = False`. If you want to display registration-protected flatpages, you need to specify an authenticated user using a `for` clause.

For example:

```html
{% get_flatpages for someuser as about_pages %}
```

If you provide an anonymous user, `get_flatpages` will behave the same as if you hadn’t provided a user – i.e., it will only show you public flatpages.

### Limiting Flatpages By Base Url

An optional argument, `starts_with`, can be applied to limit the returned pages to those beginning with a particular base URL. This argument may be passed as a string, or as a variable to be resolved from the context.

For example:

```html
{% get_flatpages '/about/' as about_pages %}
{% get_flatpages about_prefix as about_pages %}
{% get_flatpages '/about/' for someuser as about_pages %}
```

## Integrating With `Django.Contrib.Sitemaps`

::: django.contrib.flatpages.sitemaps.FlatPageSitemap

:::

The [sitemaps.FlatPageSitemap](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#django.contrib.flatpages.sitemaps.FlatPageSitemap) class looks at all publicly visible [flatpages](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#module-django.contrib.flatpages) defined for the current [SITE_ID](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SITE_ID) (see the [sites documentation](https://docs.djangoproject.com/en/5.2/ref/contrib/sites/#module-django.contrib.sites)) and creates an entry in the sitemap. These entries include only the [location](https://docs.djangoproject.com/en/5.2/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.location) attribute – not [lastmod](https://docs.djangoproject.com/en/5.2/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.lastmod), [changefreq](https://docs.djangoproject.com/en/5.2/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.changefreq) or [priority](https://docs.djangoproject.com/en/5.2/ref/contrib/sitemaps/#django.contrib.sitemaps.Sitemap.priority).

### Example

Here’s an example of a URLconf using [FlatPageSitemap](https://docs.djangoproject.com/en/5.2/ref/contrib/flatpages/#django.contrib.flatpages.sitemaps.FlatPageSitemap):

```python
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path

urlpatterns = [
    # ...
    # the sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"flatpages": FlatPageSitemap}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
```