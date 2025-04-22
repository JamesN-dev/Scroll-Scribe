# Django.urls Functions for Use in URLconfs

## path()

```python
path(route, view, kwargs=None, name=None)
```

Returns an element for inclusion in `urlpatterns`. For example:

```python
from django.urls import include, path

urlpatterns = [
    path("index/", views.index, name="main-view"),
    path("bio/<username>/", views.bio, name="bio"),
    path("articles/<slug:title>/", views.article, name="article-detail"),
    path("articles/<slug:title>/<int:section>/", views.section, name="article-section"),
    path("blog/", include("blog.urls")),
    ...
]
```

### route

The `route` argument should be a string or `gettext_lazy()` (see [Translating URL patterns](../../topics/i18n/translation/#translating-urlpatterns)) that contains a URL pattern. The string may contain angle brackets (like `<username>` above) to capture part of the URL and send it as a keyword argument to the view. The angle brackets may include a converter specification (like the `int` part of `<int:section>`) which limits the characters matched and may also change the type of the variable passed to the view. For example, `<int:section>` matches a string of decimal digits and converts the value to an `int`.

When processing a request, Django starts at the first pattern in `urlpatterns` and makes its way down the list, comparing the requested URL against each pattern until it finds one that matches. See [How Django processes a request](../../topics/http/urls/#how-django-processes-a-request) for more details.

Patterns don’t match GET and POST parameters, or the domain name. For example, in a request to `https://www.example.com/myapp/`, the URLconf will look for `myapp/`. In a request to `https://www.example.com/myapp/?page=3`, the URLconf will also look for `myapp/`.

### view

The `view` argument is a view function or the result of `as_view()` for class-based views. It can also be a `django.urls.include()`.

When Django finds a matching pattern, it calls the specified view function with an `HttpRequest` object as the first argument and any “captured” values from the route as keyword arguments.

### kwargs

The `kwargs` argument allows you to pass additional arguments to the view function or method. See [Passing extra options to view functions](../../topics/http/urls/#views-extra-options) for an example.

### name

Naming your URL lets you refer to it unambiguously from elsewhere in Django, especially from within templates. This powerful feature allows you to make global changes to the URL patterns of your project while only touching a single file.

See [Naming URL patterns](../../topics/http/urls/#naming-url-patterns) for why the `name` argument is useful.

## re_path()

```python
re_path(route, view, kwargs=None, name=None)
```

Returns an element for inclusion in `urlpatterns`. For example:

```python
from django.urls import include, re_path

urlpatterns = [
    re_path(r"^index/$", views.index, name="index"),
    re_path(r"^bio/(?P<username>\w+)/$", views.bio, name="bio"),
    re_path(r"^blog/", include("blog.urls")),
    ...
]
```

The `route` argument should be a string or `gettext_lazy()` (see [Translating URL patterns](../../topics/i18n/translation/#translating-urlpatterns)) that contains a regular expression compatible with Python’s `re` module. Strings typically use raw string syntax (`r''`) so that they can contain sequences like `\d` without the need to escape the backslash with another backslash. When a match is made, captured groups from the regular expression are passed to the view – as named arguments if the groups are named, and as positional arguments otherwise. The values are passed as strings, without any type conversion.

When a `route` ends with `$` the whole requested URL, matching against `path_info`, must match the regular expression pattern (`re.fullmatch()` is used).

The `view`, `kwargs` and `name` arguments are the same as for `path()`.

## include()

```python
include(module, namespace=None)
include(pattern_list)
include((pattern_list, app_namespace), namespace=None)
```

A function that takes a full Python import path to another URLconf module that should be “included” in this place. Optionally, the [application namespace](../../topics/http/urls/#term-application-namespace) and [instance namespace](../../topics/http/urls/#term-instance-namespace) where the entries will be included into can also be specified.

Usually, the application namespace should be specified by the included module. If an application namespace is set, the `namespace` argument can be used to set a different instance namespace.

`include()` also accepts as an argument either an iterable that returns URL patterns or a 2-tuple containing such iterable plus the names of the application namespaces.

### Parameters:

- **module** – URLconf module (or module name)
- **namespace** (*str*) – Instance namespace for the URL entries being included
- **pattern_list** – Iterable of `path()` and/or `re_path()` instances.
- **app_namespace** (*str*) – Application namespace for the URL entries being included

See [Including other URLconfs](../../topics/http/urls/#including-other-urlconfs) and [URL namespaces and included URLconfs](../../topics/http/urls/#namespaces-and-include).

## register_converter()

```python
register_converter(converter, type_name)
```

The function for registering a converter for use in `path()` `route`s.

The `converter` argument is a converter class, and `type_name` is the converter name to use in path patterns. See [Registering custom path converters](../../topics/http/urls/#registering-custom-path-converters) for an example.

> **Deprecated since version 5.1:** Overriding existing converters is deprecated.

# Django.conf.urls Functions for Use in URLconfs

## static()

```python
static.static(prefix, view=django.views.static.serve, **kwargs)
```

Helper function to return a URL pattern for serving files in debug mode:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## handler400

A callable, or a string representing the full Python import path to the view that should be called if the HTTP client has sent a request that caused an error condition and a response with a status code of 400.

By default, this is `django.views.defaults.bad_request()`. If you implement a custom view, be sure it accepts `request` and `exception` arguments and returns an `HttpResponseBadRequest`.

## handler403

A callable, or a string representing the full Python import path to the view that should be called if the user doesn’t have the permissions required to access a resource.

By default, this is `django.views.defaults.permission_denied()`. If you implement a custom view, be sure it accepts `request` and `exception` arguments and returns an `HttpResponseForbidden`.

## handler404

A callable, or a string representing the full Python import path to the view that should be called if none of the URL patterns match.

By default, this is `django.views.defaults.page_not_found()`. If you implement a custom view, be sure it accepts `request` and `exception` arguments and returns an `HttpResponseNotFound`.

## handler500

A callable, or a string representing the full Python import path to the view that should be called in case of server errors. Server errors happen when you have runtime errors in view code.

By default, this is `django.views.defaults.server_error()`. If you implement a custom view, be sure it accepts a `request` argument and returns an `HttpResponseServerError`.