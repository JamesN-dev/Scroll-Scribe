# The Django Source Code Repository

When deploying a Django application into a real production environment, you will almost always want to use [an official packaged release of Django](https://www.djangoproject.com/download/).

However, if you’d like to try out in-development code from an upcoming release or contribute to the development of Django, you’ll need to obtain a clone of Django’s source code repository.

This document covers the way the code repository is laid out and how to work with and find things in it.

## High-Level Overview

The Django source code repository uses [Git](https://git-scm.com/) to track changes to the code over time, so you’ll need a copy of the Git client (a program called `git`) on your computer, and you’ll want to familiarize yourself with the basics of how Git works.

Git’s website offers downloads for various operating systems. The site also contains vast amounts of [documentation](https://git-scm.com/doc).

The Django Git repository is located online at [github.com/django/django](https://github.com/django/django). It contains the full source code for all Django releases, which you can browse online.

The Git repository includes several [branches](https://github.com/django/django/branches):

*   `main` contains the main in-development code which will become the next packaged release of Django. This is where most development activity is focused.
*   `stable/A.B.x` are the branches where release preparation work happens. They are also used for bugfix and security releases which occur as necessary after the initial release of a feature version.

The Git repository also contains [tags](https://github.com/django/django/tags). These are the exact revisions from which packaged Django releases were produced, since version 1.0.

A number of tags also exist under the `archive/` prefix for [archived work](#archived-feature-development-work).

The source code for the [Djangoproject.com](https://www.djangoproject.com/) website can be found at [github.com/django/djangoproject.com](https://github.com/django/djangoproject.com).

## The Main Branch

If you’d like to try out the in-development code for the next release of Django, or if you’d like to contribute to Django by fixing bugs or developing new features, you’ll want to get the code from the main branch.

Note

Prior to March 2021, the main branch was called `master`.

Note that this will get *all* of Django: in addition to the top-level `django` module containing Python code, you’ll also get a copy of Django’s documentation, test suite, packaging scripts and other miscellaneous bits. Django’s code will be present in your clone as a directory named `django`.

To try out the in-development code with your own applications, place the directory containing your clone on your Python import path. Then `import` statements which look for Django will find the `django` module within your clone.

If you’re going to be working on Django’s code (say, to fix a bug or develop a new feature), you can probably stop reading here and move over to [the documentation for contributing to Django](../contributing/), which covers things like the preferred coding style and how to generate and submit a patch.

## Stable Branches

Django uses branches to prepare for releases of Django. Each major release series has its own stable branch.

These branches can be found in the repository as `stable/A.B.x` branches and will be created right after the first alpha is tagged.

For example, immediately after *Django 1.5 alpha 1* was tagged, the branch `stable/1.5.x` was created and all further work on preparing the code for the final 1.5 release was done there.

These branches also provide bugfix and security support as described in [Supported versions](../release-process/#supported-versions-policy).

For example, after the release of Django 1.5, the branch `stable/1.5.x` receives only fixes for security and critical stability bugs, which are eventually released as Django 1.5.1 and so on, `stable/1.4.x` receives only security and data loss fixes, and `stable/1.3.x` no longer receives any updates.

Historical information

This policy for handling `stable/A.B.x` branches was adopted starting with the Django 1.5 release cycle.

Previously, these branches weren’t created until right after the releases and the stabilization work occurred on the main repository branch. Thus, no new feature development work for the next release of Django could be committed until the final release happened.

For example, shortly after the release of Django 1.3 the branch `stable/1.3.x` was created. Official support for that release has expired, and so it no longer receives direct maintenance from the Django project. However, that and all other similarly named branches continue to exist, and interested community members have occasionally used them to provide unofficial support for old Django releases.

## Tags

Each Django release is tagged and signed by the releaser.

The tags can be found on GitHub’s [tags](https://github.com/django/django/tags) page.

### Archived Feature-Development Work

Historical information

Since Django moved to Git in 2012, anyone can clone the repository and create their own branches, alleviating the need for official branches in the source code repository.

The following section is mostly useful if you’re exploring the repository’s history, for example if you’re trying to understand how some features were designed.

Feature-development branches tend by their nature to be temporary. Some produce successful features which are merged back into Django’s main branch to become part of an official release, but others do not; in either case, there comes a time when the branch is no longer being actively worked on by any developer. At this point the branch is considered closed.

Django used to be maintained with the Subversion revision control system, that has no standard way of indicating this. As a workaround, branches of Django which are closed and no longer maintained were moved into `attic`.

A number of tags exist under the `archive/` prefix to maintain a reference to this and other work of historical interest.

The following tags under the `archive/attic/` prefix reference the tip of branches whose code eventually became part of Django itself:

*   `boulder-oracle-sprint`: Added support for Oracle databases to Django’s object-relational mapper. This has been part of Django since the 1.0 release.
*   `gis`: Added support for geographic/spatial queries to Django’s object-relational mapper. This has been part of Django since the 1.0 release, as the bundled application `django.contrib.gis`.
*   `i18n`: Added [internationalization support](../../topics/i18n/) to Django. This has been part of Django since the 0.90 release.
*   `magic-removal`: A major refactoring of both the internals and public APIs of Django’s object-relational mapper. This has been part of Django since the 0.95 release.
*   `multi-auth`: A refactoring of [Django’s bundled authentication framework](../../topics/auth/) which added support for [authentication backends](../../topics/auth/customizing/#authentication-backends). This has been part of Django since the 0.95 release.
*   `new-admin`: A refactoring of [Django’s bundled administrative application](../../ref/contrib/admin/). This became part of Django as of the 0.91 release, but was superseded by another refactoring (see next listing) prior to the Django 1.0 release.
*   `newforms-admin`: The second refactoring of Django’s bundled administrative application. This became part of Django as of the 1.0 release, and is the basis of the current incarnation of `django.contrib.admin`.
*   `queryset-refactor`: A refactoring of the internals of Django’s object-relational mapper. This became part of Django as of the 1.0 release.
*   `unicode`: A refactoring of Django’s internals to consistently use Unicode-based strings in most places within Django and Django applications. This became part of Django as of the 1.0 release.

Additionally, the following tags under the `archive/attic/` prefix reference the tips of branches that were closed, but whose code was never merged into Django, and the features they aimed to implement were never finished:

*   `full-history`
*   `generic-auth`
*   `multiple-db-support`
*   `per-object-permissions`
*   `schema-evolution`
*   `schema-evolution-ng`
*   `search-api`
*   `sqlalchemy`

Finally, under the `archive/` prefix, the repository contains `soc20XX/<project>` tags referencing the tip of branches that were used by students who worked on Django during the 2009 and 2010 Google Summer of Code programs.