# How to manage static files (e.g. images, JavaScript, CSS)

Websites generally need to serve additional files such as images, JavaScript, or CSS. In Django, we refer to these files as “static files”. Django provides [`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles) to help you manage them.

This page describes how you can serve these static files.

## Configuring static files

1.  Make sure that [`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles) is included in your [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS).
2.  In your settings file, define [`STATIC_URL`](../../ref/settings/#std-setting-STATIC_URL), for example:

    ```
    STATIC_URL = "static/"
    ```

3.  In your templates, use the [`static`](../../ref/templates/builtins/#std-templatetag-static) template tag to build the URL for the given relative path using the configured `staticfiles` [`STORAGES`](../../ref/settings/#std-setting-STORAGES) alias.

    ```html+django
    {% load static %}
    <img src="{% static 'my_app/example.jpg' %}" alt="My image">
    ```

4.  Store your static files in a folder called `static` in your app. For example `my_app/static/my_app/example.jpg`.

    Serving the files

    In addition to these configuration steps, you’ll also need to actually serve the static files.

    During development, if you use [`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles), this will be done automatically by [`runserver`](../../ref/django-admin/#django-admin-runserver) when [`DEBUG`](../../ref/settings/#std-setting-DEBUG) is set to `True` (see [`django.contrib.staticfiles.views.serve()`](../../ref/contrib/staticfiles/#django.contrib.staticfiles.views.serve)).

    This method is **grossly inefficient** and probably **insecure**, so it is **unsuitable for production**.

    See [How to deploy static files](deployment/) for proper strategies to serve static files in production environments.

Your project will probably also have static assets that aren’t tied to a particular app. In addition to using a `static/` directory inside your apps, you can define a list of directories ([`STATICFILES_DIRS`](../../ref/settings/#std-setting-STATICFILES_DIRS)) in your settings file where Django will also look for static files. For example:

```python
STATICFILES_DIRS = [
    BASE_DIR / "static",
    "/var/www/static/",
]
```

See the documentation for the [`STATICFILES_FINDERS`](../../ref/settings/#std-setting-STATICFILES_FINDERS) setting for details on how `staticfiles` finds your files.

Static file namespacing

Now we *might* be able to get away with putting our static files directly in `my_app/static/` (rather than creating another `my_app` subdirectory), but it would actually be a bad idea. Django will use the first static file it finds whose name matches, and if you had a static file with the same name in a *different* application, Django would be unable to distinguish between them. We need to be able to point Django at the right one, and the best way to ensure this is by *namespacing* them. That is, by putting those static files inside *another* directory named for the application itself.

You can namespace static assets in [`STATICFILES_DIRS`](../../ref/settings/#std-setting-STATICFILES_DIRS) by specifying [prefixes](../../ref/settings/#staticfiles-dirs-prefixes).

## Serving static files during development

If you use [`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles) as explained above, [`runserver`](../../ref/django-admin/#django-admin-runserver) will do this automatically when [`DEBUG`](../../ref/settings/#std-setting-DEBUG) is set to `True`. If you don’t have `django.contrib.staticfiles` in [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS), you can still manually serve static files using the [`django.views.static.serve()`](../../ref/views/#django.views.static.serve) view.

This is not suitable for production use! For some common deployment strategies, see [How to deploy static files](deployment/).

For example, if your [`STATIC_URL`](../../ref/settings/#std-setting-STATIC_URL) is defined as `static/`, you can do this by adding the following snippet to your `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

Note

This helper function works only in debug mode and only if the given prefix is local (e.g. `static/`) and not a URL (e.g. `http://static.example.com/`).

Also this helper function only serves the actual [`STATIC_ROOT`](../../ref/settings/#std-setting-STATIC_ROOT) folder; it doesn’t perform static files discovery like [`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles).

Finally, static files are served via a wrapper at the WSGI application layer. As a consequence, static files requests do not pass through the normal [middleware chain](../../topics/http/middleware/).

## Serving files uploaded by a user during development

During development, you can serve user-uploaded media files from [`MEDIA_ROOT`](../../ref/settings/#std-setting-MEDIA_ROOT) using the [`django.views.static.serve()`](../../ref/views/#django.views.static.serve) view.

This is not suitable for production use! For some common deployment strategies, see [How to deploy static files](deployment/).

For example, if your [`MEDIA_URL`](../../ref/settings/#std-setting-MEDIA_URL) is defined as `media/`, you can do this by adding the following snippet to your [`ROOT_URLCONF`](../../ref/settings/#std-setting-ROOT_URLCONF):

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Note

This helper function works only in debug mode and only if the given prefix is local (e.g. `media/`) and not a URL (e.g. `http://media.example.com/`).

## Testing

When running tests that use actual HTTP requests instead of the built-in testing client (i.e. when using the built-in [`LiveServerTestCase`](../../topics/testing/tools/#django.test.LiveServerTestCase)) the static assets need to be served along the rest of the content so the test environment reproduces the real one as faithfully as possible, but `LiveServerTestCase` has only very basic static file-serving functionality: It doesn’t know about the finders feature of the `staticfiles` application and assumes the static content has already been collected under [`STATIC_ROOT`](../../ref/settings/#std-setting-STATIC_ROOT).

Because of this, `staticfiles` ships its own [`django.contrib.staticfiles.testing.StaticLiveServerTestCase`](../../ref/contrib/staticfiles/#django.contrib.staticfiles.testing.StaticLiveServerTestCase), a subclass of the built-in one that has the ability to transparently serve all the assets during execution of these tests in a way very similar to what we get at development time with `DEBUG = True`, i.e. without having to collect them using [`collectstatic`](../../ref/contrib/staticfiles/#django-admin-collectstatic) first.

## Deployment

[`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles) provides a convenience management command for gathering static files in a single directory so you can serve them easily.

1.  Set the [`STATIC_ROOT`](../../ref/settings/#std-setting-STATIC_ROOT) setting to the directory from which you’d like to serve these files, for example:

    ```python
    STATIC_ROOT = "/var/www/example.com/static/"
    ```

2.  Run the [`collectstatic`](../../ref/contrib/staticfiles/#django-admin-collectstatic) management command:

    ```bash
    $ python manage.py collectstatic
    ```

    This will copy all files from your static folders into the [`STATIC_ROOT`](../../ref/settings/#std-setting-STATIC_ROOT) directory.

3.  Use a web server of your choice to serve the files. [How to deploy static files](deployment/) covers some common deployment strategies for static files.

## Learn more

This document has covered the basics and some common usage patterns. For complete details on all the settings, commands, template tags, and other pieces included in [`django.contrib.staticfiles`](../../ref/contrib/staticfiles/#module-django.contrib.staticfiles), see [the staticfiles reference](../../ref/contrib/staticfiles/).