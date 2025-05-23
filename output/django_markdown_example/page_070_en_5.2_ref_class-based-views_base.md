# Base Views

The following three classes provide much of the functionality needed to create Django views. You may think of them as *parent* views, which can be used by themselves or inherited from. They may not provide all the capabilities required for projects, in which case there are Mixins and Generic class-based views.

Many of Django’s built-in class-based views inherit from other class-based views or various mixins. Because this inheritance chain is very important, the ancestor classes are documented under the section title of **Ancestors (MRO)**. MRO is an acronym for Method Resolution Order.

## `View`

*class* `django.views.generic.base.View`

The base view class. All other class-based views inherit from this base class. It isn’t strictly a generic view and thus can also be imported from `django.views`.

**Method Flowchart**

1.  [`setup()`](#django.views.generic.base.View.setup)
2.  [`dispatch()`](#django.views.generic.base.View.dispatch)
3.  [`http_method_not_allowed()`](#django.views.generic.base.View.http_method_not_allowed)
4.  [`options()`](#django.views.generic.base.View.options)

**Example views.py**:

```python
from django.http import HttpResponse
from django.views import View

class MyView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, World!")
```

**Example urls.py**:

```python
from django.urls import path
from myapp.views import MyView

urlpatterns = [
    path("mine/", MyView.as_view(), name="my-view"),
]
```

**Attributes**

`http_method_names`

The list of HTTP method names that this view will accept.

Default:

```python
["get", "post", "put", "patch", "delete", "head", "options", "trace"]
```

**Methods**

*classmethod* `as_view`(*\*\*initkwargs*)

Returns a callable view that takes a request and returns a response:

```python
response = MyView.as_view()(request)
```

The returned view has `view_class` and `view_initkwargs` attributes.

When the view is called during the request/response cycle, the [`setup()`](#django.views.generic.base.View.setup) method assigns the [`HttpRequest`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpRequest) to the view’s `request` attribute, and any positional and/or keyword arguments [captured from the URL pattern](https://docs.djangoproject.com/en/5.2/topics/http/urls/#how-django-processes-a-request) to the `args` and `kwargs` attributes, respectively. Then [`dispatch()`](#django.views.generic.base.View.dispatch) is called.

If a `View` subclass defines asynchronous (`async def`) method handlers, `as_view()` will mark the returned callable as a coroutine function. An `ImproperlyConfigured` exception will be raised if both asynchronous (`async def`) and synchronous (`def`) handlers are defined on a single view-class.

`setup`(*request*, *\*args*, *\*\*kwargs*)

Performs key view initialization prior to [`dispatch()`](#django.views.generic.base.View.dispatch).

Assigns the [`HttpRequest`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpRequest) to the view’s `request` attribute, and any positional and/or keyword arguments [captured from the URL pattern](https://docs.djangoproject.com/en/5.2/topics/http/urls/#how-django-processes-a-request) to the `args` and `kwargs` attributes, respectively.

If overriding this method, you must call `super()`.

`dispatch`(*request*, *\*args*, *\*\*kwargs*)

The `view` part of the view – the method that accepts a `request` argument plus arguments, and returns an HTTP response.

The default implementation will inspect the HTTP method and attempt to delegate to a method that matches the HTTP method; a `GET` will be delegated to `get()`, a `POST` to `post()`, and so on.

By default, a `HEAD` request will be delegated to `get()`. If you need to handle `HEAD` requests in a different way than `GET`, you can override the `head()` method. See [Supporting other HTTP methods](https://docs.djangoproject.com/en/5.2/topics/class-based-views/#supporting-other-http-methods) for an example.

`http_method_not_allowed`(*request*, *\*args*, *\*\*kwargs*)

If the view was called with an HTTP method it doesn’t support, this method is called instead.

The default implementation returns `HttpResponseNotAllowed` with a list of allowed methods in plain text.

`options`(*request*, *\*args*, *\*\*kwargs*)

Handles responding to requests for the OPTIONS HTTP verb. Returns a response with the `Allow` header containing a list of the view’s allowed HTTP method names.

If the other HTTP methods handlers on the class are asynchronous (`async def`) then the response will be wrapped in a coroutine function for use with `await`.

## `TemplateView`

*class* `django.views.generic.base.TemplateView`

Renders a given template, with the context containing parameters captured in the URL.

**Ancestors (MRO)**

This view inherits methods and attributes from the following views:

*   [`django.views.generic.base.TemplateResponseMixin`](https://docs.djangoproject.com/en/5.2/ref/mixins-simple/#django.views.generic.base.TemplateResponseMixin)
*   [`django.views.generic.base.ContextMixin`](https://docs.djangoproject.com/en/5.2/ref/mixins-simple/#django.views.generic.base.ContextMixin)
*   [`django.views.generic.base.View`](#django.views.generic.base.View)

**Method Flowchart**

1.  [`setup()`](#django.views.generic.base.View.setup)
2.  [`dispatch()`](#django.views.generic.base.View.dispatch)
3.  [`http_method_not_allowed()`](#django.views.generic.base.View.http_method_not_allowed)
4.  [`get_context_data()`](https://docs.djangoproject.com/en/5.2/ref/mixins-simple/#django.views.generic.base.ContextMixin.get_context_data)

**Example views.py**:

```python
from django.views.generic.base import TemplateView
from articles.models import Article

class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_articles"] = Article.objects.all()[:5]
        return context
```

**Example urls.py**:

```python
from django.urls import path
from myapp.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
```

**Context**

*   Populated (through [`ContextMixin`](https://docs.djangoproject.com/en/5.2/ref/mixins-simple/#django.views.generic.base.ContextMixin)) with the keyword arguments captured from the URL pattern that served the view.
*   You can also add context using the [`extra_context`](https://docs.djangoproject.com/en/5.2/ref/mixins-simple/#django.views.generic.base.ContextMixin.extra_context) keyword argument for [`as_view()`](#django.views.generic.base.View.as_view).

## `RedirectView`

*class* `django.views.generic.base.RedirectView`

Redirects to a given URL.

The given URL may contain dictionary-style string formatting, which will be interpolated against the parameters captured in the URL. Because keyword interpolation is *always* done (even if no arguments are passed in), any `"%"` characters in the URL must be written as `%%` so that Python will convert them to a single percent sign on output.

If the given URL is `None`, Django will return an `HttpResponseGone` (410).

**Ancestors (MRO)**

This view inherits methods and attributes from the following view:

*   [`django.views.generic.base.View`](#django.views.generic.base.View)

**Method Flowchart**

1.  [`setup()`](#django.views.generic.base.View.setup)
2.  [`dispatch()`](#django.views.generic.base.View.dispatch)
3.  [`http_method_not_allowed()`](#django.views.generic.base.View.http_method_not_allowed)
4.  [`get_redirect_url()`](#django.views.generic.base.RedirectView.get_redirect_url)

**Example views.py**:

```python
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from articles.models import Article

class ArticleCounterRedirectView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = "article-detail"

    def get_redirect_url(self, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs["pk"])
        article.update_counter()
        return super().get_redirect_url(*args, **kwargs)
```

**Example urls.py**:

```python
from django.urls import path
from django.views.generic.base import RedirectView
from article.views import ArticleCounterRedirectView, ArticleDetailView

urlpatterns = [
    path(
        "counter/<int:pk>/",
        ArticleCounterRedirectView.as_view(),
        name="article-counter",
    ),
    path("details/<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path(
        "go-to-django/",
        RedirectView.as_view(url="https://www.djangoproject.com/"),
        name="go-to-django",
    ),
]
```

**Attributes**

`url`

The URL to redirect to, as a string. Or `None` to raise a 410 (Gone) HTTP error.

`pattern_name`

The name of the URL pattern to redirect to. Reversing will be done using the same args and kwargs as are passed in for this view.

`permanent`

Whether the redirect should be permanent. The only difference here is the HTTP status code returned. If `True`, then the redirect will use status code 301. If `False`, then the redirect will use status code 302. By default, `permanent` is `False`.

`query_string`

Whether to pass along the GET query string to the new location. If `True`, then the query string is appended to the URL. If `False`, then the query string is discarded. By default, `query_string` is `False`.

**Methods**

`get_redirect_url`(*\*args*, *\*\*kwargs*)

Constructs the target URL for redirection.

The `args` and `kwargs` arguments are positional and/or keyword arguments [captured from the URL pattern](https://docs.djangoproject.com/en/5.2/topics/http/urls/#how-django-processes-a-request), respectively.

The default implementation uses `url` as a starting string and performs expansion of `%` named parameters in that string using the named groups captured in the URL.

If `url` is not set, `get_redirect_url()` tries to reverse the `pattern_name` using what was captured in the URL (both named and unnamed groups are used).

If requested by `query_string`, it will also append the query string to the generated URL. Subclasses may implement any behavior they wish, as long as the method returns a redirect-ready URL string.