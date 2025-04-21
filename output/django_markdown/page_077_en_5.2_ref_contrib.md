# Contrib Packages

Django aims to follow Python’s [“batteries included” philosophy](https://docs.python.org/3/tutorial/stdlib.html#tut-batteries-included). It ships with a variety of extra, optional tools that solve common web development problems.

This code lives in [django/contrib](https://github.com/django/django/blob/main/django/contrib) in the Django distribution. This document gives a rundown of the packages in `contrib`, along with any dependencies those packages have.

Including `contrib` packages in `INSTALLED_APPS`

For most of these add-ons – specifically, the add-ons that include either models or template tags – you’ll need to add the package name (e.g., `'django.contrib.redirects'`) to your [`INSTALLED_APPS`](../settings/#std-setting-INSTALLED_APPS) setting and rerun `manage.py migrate`.

- [The Django admin site](admin/)
- [`django.contrib.auth`](auth/)
- [The contenttypes framework](contenttypes/)
- [The flatpages app](flatpages/)
- [GeoDjango](gis/)
- [`django.contrib.humanize`](humanize/)
- [The messages framework](messages/)
- [`django.contrib.postgres`](postgres/)
- [The redirects app](redirects/)
- [The sitemap framework](sitemaps/)
- [The “sites” framework](sites/)
- [The `staticfiles` app](staticfiles/)
- [The syndication feed framework](syndication/)

## Admin

The automatic Django administrative interface. For more information, see [Tutorial 2](../../intro/tutorial02/) and the [admin documentation](admin/).

Requires the [auth](#auth) and [contenttypes](#contenttypes) contrib packages to be installed.

## Auth

Django’s authentication framework.

See [User authentication in Django](../../topics/auth/).

## Contenttypes

A light framework for hooking into “types” of content, where each installed Django model is a separate content type.

See the [contenttypes documentation](contenttypes/).

## Flatpages

A framework for managing “flat” HTML content in a database.

See the [flatpages documentation](flatpages/).

Requires the [sites](#sites) contrib package to be installed as well.

## Gis

A world-class geospatial framework built on top of Django, that enables storage, manipulation and display of spatial data.

See the [GeoDjango](gis/) documentation for more.

## Humanize

A set of Django template filters useful for adding a “human touch” to data.

See the [humanize documentation](humanize/).

## Messages

A framework for storing and retrieving temporary cookie- or session-based messages

See the [messages documentation](messages/).

## Postgres

A collection of PostgreSQL specific features.

See the [contrib.postgres documentation](postgres/).

## Redirects

A framework for managing redirects.

See the [redirects documentation](redirects/).

## Sessions

A framework for storing data in anonymous sessions.

See the [sessions documentation](../../topics/http/sessions/).

## Sites

A light framework that lets you operate multiple websites off of the same database and Django installation. It gives you hooks for associating objects to one or more sites.

See the [sites documentation](sites/).

## Sitemaps

A framework for generating Google sitemap XML files.

See the [sitemaps documentation](sitemaps/).

## Syndication

A framework for generating syndication feeds, in RSS and Atom, quite easily.

See the [syndication documentation](syndication/).