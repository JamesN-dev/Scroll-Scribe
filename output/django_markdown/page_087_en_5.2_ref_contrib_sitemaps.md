# The Sitemap Framework

Django comes with a high-level sitemap-generating framework to create [sitemap](https://www.sitemaps.org/) XML files.

## Overview

A sitemap is an XML file on your website that tells search-engine indexers how frequently your pages change and how “important” certain pages are in relation to other pages on your site. This information helps search engines index your site.

The Django sitemap framework automates the creation of this XML file by letting you express this information in Python code.

It works much like Django’s [syndication framework](../syndication/). To create a sitemap, write a `Sitemap` class and point to it in your [URLconf](../../../topics/http/urls/).

## Installation

To install the sitemap app, follow these steps:

1.  Add `'django.contrib.sitemaps'` to your [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) setting.
2.  Make sure your [`TEMPLATES`](../../settings/#std-setting-TEMPLATES) setting contains a `DjangoTemplates` backend whose `APP_DIRS` options is set to `True`. It’s in there by default, so you’ll only need to change this if you’ve changed that setting.
3.  Make sure you’ve installed the [sites framework](../sites/).

(Note: The sitemap application doesn’t install any database tables. The only reason it needs to go into [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) is so that the [`Loader()`](../../templates/api/#django.template.loaders.app_directories.Loader) template loader can find the default templates.)

## Initialization

`views.sitemap`(request, sitemaps, section=None, template_name='sitemap.xml', content_type='application/xml')

To activate sitemap generation on your Django site, add this line to your [URLconf](../../../topics/http/urls/):

```python
from django.contrib.sitemaps.views import sitemap

path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
)
```

This tells Django to build a sitemap when a client accesses `/sitemap.xml`.

The name of the sitemap file is not important, but the location is. Search engines will only index links in your sitemap for the current URL level and below. For instance, if `sitemap.xml` lives in your root directory, it may reference any URL in your site. However, if your sitemap lives at `/content/sitemap.xml`, it may only reference URLs that begin with `/content/`.

The sitemap view takes an extra, required argument: `{'sitemaps': sitemaps}`. `sitemaps` should be a dictionary that maps a short section label (e.g., `blog` or `news`) to its `Sitemap` class (e.g., `BlogSitemap` or `NewsSitemap`). It may also map to an *instance* of a `Sitemap` class (e.g., `BlogSitemap(some_var)`).

## `Sitemap` Classes

A `Sitemap` class is a Python class that represents a “section” of entries in your sitemap. For example, one `Sitemap` class could represent all the entries of your blog, while another could represent all of the events in your events calendar.

In the simplest case, all these sections get lumped together into one `sitemap.xml`, but it’s also possible to use the framework to generate a sitemap index that references individual sitemap files, one per section. (See [Creating A Sitemap Index](#creating-a-sitemap-index) below.)

`Sitemap` classes must subclass `django.contrib.sitemaps.Sitemap`. They can live anywhere in your codebase.

## An Example

Let’s assume you have a blog system, with an `Entry` model, and you want your sitemap to include all the links to your individual blog entries. Here’s how your sitemap class might look:

```python
from django.contrib.sitemaps import Sitemap
from blog.models import Entry

class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Entry.objects.filter(is_draft=False)

    def lastmod(self, obj):
        return obj.pub_date
```

Note:

*   [`changefreq`](#django.contrib.sitemaps.Sitemap.changefreq) and [`priority`](#django.contrib.sitemaps.Sitemap.priority) are class attributes corresponding to `<changefreq>` and `<priority>` elements, respectively. They can be made callable as functions, as [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod) was in the example.
*   [`items()`](#django.contrib.sitemaps.Sitemap.items) is a method that returns a [sequence](https://docs.python.org/3/glossary.html#term-sequence) or `QuerySet` of objects. The objects returned will get passed to any callable methods corresponding to a sitemap property ([`location`](#django.contrib.sitemaps.Sitemap.location), [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod), [`changefreq`](#django.contrib.sitemaps.Sitemap.changefreq), and [`priority`](#django.contrib.sitemaps.Sitemap.priority)).
*   [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod) should return a [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime).
*   There is no [`location`](#django.contrib.sitemaps.Sitemap.location) method in this example, but you can provide it in order to specify the URL for your object. By default, [`location()`](#django.contrib.sitemaps.Sitemap.location) calls `get_absolute_url()` on each object and returns the result.

## `Sitemap` Class Reference

### *class* `Sitemap`

A `Sitemap` class can define the following methods/attributes:

#### `items`

**Required.** A method that returns a [sequence](https://docs.python.org/3/glossary.html#term-sequence) or `QuerySet` of objects. The framework doesn’t care what *type* of objects they are; all that matters is that these objects get passed to the [`location()`](#django.contrib.sitemaps.Sitemap.location), [`lastmod()`](#django.contrib.sitemaps.Sitemap.lastmod), [`changefreq()`](#django.contrib.sitemaps.Sitemap.changefreq) and [`priority()`](#django.contrib.sitemaps.Sitemap.priority) methods.

#### `location`

**Optional.** Either a method or attribute.

If it’s a method, it should return the absolute path for a given object as returned by [`items()`](#django.contrib.sitemaps.Sitemap.items).

If it’s an attribute, its value should be a string representing an absolute path to use for *every* object returned by [`items()`](#django.contrib.sitemaps.Sitemap.items).

In both cases, “absolute path” means a URL that doesn’t include the protocol or domain. Examples:

*   Good: `'/foo/bar/'`
*   Bad: `'example.com/foo/bar/'`
*   Bad: `'https://example.com/foo/bar/'`

If [`location`](#django.contrib.sitemaps.Sitemap.location) isn’t provided, the framework will call the `get_absolute_url()` method on each object as returned by [`items()`](#django.contrib.sitemaps.Sitemap.items).

To specify a protocol other than `'http'`, use [`protocol`](#django.contrib.sitemaps.Sitemap.protocol).

#### `lastmod`

**Optional.** Either a method or attribute.

If it’s a method, it should take one argument – an object as returned by [`items()`](#django.contrib.sitemaps.Sitemap.items) – and return that object’s last-modified date/time as a [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime).

If it’s an attribute, its value should be a [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime) representing the last-modified date/time for *every* object returned by [`items()`](#django.contrib.sitemaps.Sitemap.items).

If all items in a sitemap have a [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod), the sitemap generated by [`views.sitemap()`](#django.contrib.sitemaps.views.sitemap) will have a `Last-Modified` header equal to the latest `lastmod`. You can activate the [ConditionalGetMiddleware](../../middleware/#django.middleware.http.ConditionalGetMiddleware) to make Django respond appropriately to requests with an `If-Modified-Since` header which will prevent sending the sitemap if it hasn’t changed.

#### `paginator`

**Optional.**

This property returns a [Paginator](../../paginator/#django.core.paginator.Paginator) for [`items()`](#django.contrib.sitemaps.Sitemap.items). If you generate sitemaps in a batch you may want to override this as a cached property in order to avoid multiple `items()` calls.

#### `changefreq`

**Optional.** Either a method or attribute.

If it’s a method, it should take one argument – an object as returned by [`items()`](#django.contrib.sitemaps.Sitemap.items) – and return that object’s change frequency as a string.

If it’s an attribute, its value should be a string representing the change frequency of *every* object returned by [`items()`](#django.contrib.sitemaps.Sitemap.items).

Possible values for [`changefreq`](#django.contrib.sitemaps.Sitemap.changefreq), whether you use a method or attribute, are:

*   `'always'`
*   `'hourly'`
*   `'daily'`
*   `'weekly'`
*   `'monthly'`
*   `'yearly'`
*   `'never'`

#### `priority`

**Optional.** Either a method or attribute.

If it’s a method, it should take one argument – an object as returned by [`items()`](#django.contrib.sitemaps.Sitemap.items) – and return that object’s priority as either a string or float.

If it’s an attribute, its value should be either a string or float representing the priority of *every* object returned by [`items()`](#django.contrib.sitemaps.Sitemap.items).

Example values for [`priority`](#django.contrib.sitemaps.Sitemap.priority): `0.4`, `1.0`. The default priority of a page is `0.5`. See the [sitemaps.org documentation](https://www.sitemaps.org/protocol.html#prioritydef) for more.

#### `protocol`

**Optional.**

This attribute defines the protocol (`'http'` or `'https'`) of the URLs in the sitemap. If it isn’t set, the protocol with which the sitemap was requested is used. If the sitemap is built outside the context of a request, the default is `'https'`.

#### `limit`

**Optional.**

This attribute defines the maximum number of URLs included on each page of the sitemap. Its value should not exceed the default value of `50000`, which is the upper limit allowed in the [Sitemaps protocol](https://www.sitemaps.org/protocol.html#index).

#### `i18n`

**Optional.**

A boolean attribute that defines if the URLs of this sitemap should be generated using all of your [`LANGUAGES`](../../settings/#std-setting-LANGUAGES). The default is `False`.

#### `languages`

**Optional.**

A [sequence](https://docs.python.org/3/glossary.html#term-sequence) of [language codes](../../../topics/i18n/#term-language-code) to use for generating alternate links when [`i18n`](#django.contrib.sitemaps.Sitemap.i18n) is enabled. Defaults to [`LANGUAGES`](../../settings/#std-setting-LANGUAGES).

#### `alternates`

**Optional.**

A boolean attribute. When used in conjunction with [`i18n`](#django.contrib.sitemaps.Sitemap.i18n) generated URLs will each have a list of alternate links pointing to other language versions using the [hreflang attribute](https://developers.google.com/search/docs/advanced/crawling/localized-versions). The default is `False`.

#### `x_default`

**Optional.**

A boolean attribute. When `True` the alternate links generated by [`alternates`](#django.contrib.sitemaps.Sitemap.alternates) will contain a `hreflang="x-default"` fallback entry with a value of [`LANGUAGE_CODE`](../../settings/#std-setting-LANGUAGE_CODE). The default is `False`.

#### `get_latest_lastmod()`

**Optional.** A method that returns the latest value returned by [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod). This function is used to add the `lastmod` attribute to [Sitemap index context variables](#sitemap-index-context-variables).

By default `get_latest_lastmod()` returns:

*   If [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod) is an attribute: [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod).
*   If [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod) is a method: The latest `lastmod` returned by calling the method with all items returned by `Sitemap.items()`.

#### `get_languages_for_item`(item)

**Optional.** A method that returns the sequence of language codes for which the item is displayed. By default `get_languages_for_item()` returns [`languages`](#django.contrib.sitemaps.Sitemap.languages).

## Shortcuts

The sitemap framework provides a convenience class for a common case:

### *class* `GenericSitemap`(info_dict, priority=None, changefreq=None, protocol=None)

The `django.contrib.sitemaps.GenericSitemap` class allows you to create a sitemap by passing it a dictionary which has to contain at least a `queryset` entry. This queryset will be used to generate the items of the sitemap. It may also have a `date_field` entry that specifies a date field for objects retrieved from the `queryset`. This will be used for the [`lastmod`](#django.contrib.sitemaps.Sitemap.lastmod) attribute and `get_latest_lastmod()` methods in the in the generated sitemap.

The [`priority`](#django.contrib.sitemaps.Sitemap.priority), [`changefreq`](#django.contrib.sitemaps.Sitemap.changefreq), and [`protocol`](#django.contrib.sitemaps.Sitemap.protocol) keyword arguments allow specifying these attributes for all URLs.

### Example

Here’s an example of a [URLconf](../../../topics/http/urls/) using `GenericSitemap`:

```python
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from blog.models import Entry

info_dict = {
    "queryset": Entry.objects.all(),
    "date_field": "pub_date",
}

urlpatterns = [
    # some generic view using info_dict
    # ...
    # the sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"blog": GenericSitemap(info_dict, priority=0.6)}},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
```

## Sitemap For Static Views

Often you want the search engine crawlers to index views which are neither object detail pages nor flatpages. The solution is to explicitly list URL names for these views in `items` and call [`reverse()`](../../urlresolvers/#django.urls.reverse) in the `location` method of the sitemap. For example:

```python
# sitemaps.py
from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["main", "about", "license"]

    def location(self, item):
        return reverse(item)

# urls.py
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from .sitemaps import StaticViewSitemap
from . import views

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("", views.main, name="main"),
    path("about/", views.about, name="about"),
    path("license/", views.license, name="license"),
    # ...
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
```

## Creating A Sitemap Index

`views.index`(request, sitemaps, template_name='sitemap_index.xml', content_type='application/xml', sitemap_url_name='django.contrib.sitemaps.views.sitemap')

The sitemap framework also has the ability to create a sitemap index that references individual sitemap files, one per each section defined in your `sitemaps` dictionary. The only differences in usage are:

*   You use two views in your URLconf: [`django.contrib.sitemaps.views.index()`](#django.contrib.sitemaps.views.index) and [`django.contrib.sitemaps.views.sitemap()`](#django.contrib.sitemaps.views.sitemap).
*   The [`django.contrib.sitemaps.views.sitemap()`](#django.contrib.sitemaps.views.sitemap) view should take a `section` keyword argument.

Here’s what the relevant URLconf lines would look like for the example above:

```python
from django.contrib.sitemaps import views

urlpatterns = [
    path(
        "sitemap.xml",
        views.index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
```

This will automatically generate a `sitemap.xml` file that references both `sitemap-flatpages.xml` and `sitemap-blog.xml`. The `Sitemap` classes and the `sitemaps` dict don’t change at all.

If all sitemaps have a `lastmod` returned by [`Sitemap.get_latest_lastmod()`](#django.contrib.sitemaps.Sitemap.get_latest_lastmod) the sitemap index will have a `Last-Modified` header equal to the latest `lastmod`.

You should create an index file if one of your sitemaps has more than 50,000 URLs. In this case, Django will automatically paginate the sitemap, and the index will reflect that.

If you’re not using the vanilla sitemap view – for example, if it’s wrapped with a caching decorator – you must name your sitemap view and pass `sitemap_url_name` to the index view:

```python
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path(
        "sitemap.xml",
        cache_page(86400)(sitemaps_views.index),
        {"sitemaps": sitemaps, "sitemap_url_name": "sitemaps"},
    ),
    path(
        "sitemap-<section>.xml",
        cache_page(86400)(sitemaps_views.sitemap),
        {"sitemaps": sitemaps},
        name="sitemaps",
    ),
]
```

## Template Customization

If you wish to use a different template for each sitemap or sitemap index available on your site, you may specify it by passing a `template_name` parameter to the `sitemap` and `index` views via the URLconf:

```python
from django.contrib.sitemaps import views

urlpatterns = [
    path(
        "custom-sitemap.xml",
        views.index,
        {"sitemaps": sitemaps, "template_name": "custom_sitemap.html"},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "custom-sitemap-<section>.xml",
        views.sitemap,
        {"sitemaps": sitemaps, "template_name": "custom_sitemap.html"},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
```

These views return `TemplateResponse` instances which allow you to easily customize the response data before rendering. For more details, see the [TemplateResponse documentation](../../template-response/).

### Context Variables

When customizing the templates for the [`index()`](#django.contrib.sitemaps.views.index) and [`sitemap()`](#django.contrib.sitemaps.views.sitemap) views, you can rely on the following context variables.

### Index

The variable `sitemaps` is a list of objects containing the `location` and `lastmod` attribute for each of the sitemaps. Each URL exposes the following attributes:

*   `location`: The location (url & page) of the sitemap.
*   `lastmod`: Populated by the [`get_latest_lastmod()`](#django.contrib.sitemaps.Sitemap.get_latest_lastmod) method for each sitemap.

### Sitemap

The variable `urlset` is a list of URLs that should appear in the sitemap. Each URL exposes attributes as defined in the `Sitemap` class:

*   `alternates`
*   `changefreq`
*   `item`
*   `lastmod`
*   `location`
*   `priority`

The `alternates` attribute is available when [`i18n`](#django.contrib.sitemaps.Sitemap.i18n) and [`alternates`](#django.contrib.sitemaps.Sitemap.alternates) are enabled. It is a list of other language versions, including the optional [`x_default`](#django.contrib.sitemaps.Sitemap.x_default) fallback, for each URL. Each alternate is a dictionary with `location` and `lang_code` keys.

The `item` attribute has been added for each URL to allow more flexible customization of the templates, such as [Google news sitemaps](https://support.google.com/news/publisher-center/answer/9606710). Assuming Sitemap’s [`items()`](#django.contrib.sitemaps.Sitemap.items) would return a list of items with `publication_data` and a `tags` field something like this would generate a Google News compatible sitemap:

```html
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="https://www.google.com/schemas/sitemap-news/0.9">
    {% spaceless %}
    {% for url in urlset %}
    <url>
        <loc>{{ url.location }}</loc>
        {% if url.lastmod %}<lastmod>{{ url.lastmod|date:"Y-m-d" }}</lastmod>{% endif %}
        {% if url.changefreq %}<changefreq>{{ url.changefreq }}</changefreq>{% endif %}
        {% if url.priority %}<priority>{{ url.priority }}</priority>{% endif %}
        <news:news>
            {% if url.item.publication_date %}<news:publication_date>{{ url.item.publication_date|date:"Y-m-d" }}</news:publication_date>{% endif %}
            {% if url.item.tags %}<news:keywords>{{ url.item.tags }}</news:keywords>{% endif %}
        </news:news>
    </url>
    {% endfor %}
    {% endspaceless %}
</urlset>
```