# Advanced Tutorial: How to Write Reusable Apps

This advanced tutorial begins where [Tutorial 8](../tutorial08/) left off. We’ll be turning our web-poll into a standalone Python package you can reuse in new projects and share with other people.

If you haven’t recently completed Tutorials 1–8, we encourage you to review these so that your example project matches the one described below.

## Reusability Matters

It’s a lot of work to design, build, test and maintain a web application. Many Python and Django projects share common problems. Wouldn’t it be great if we could save some of this repeated work?

Reusability is the way of life in Python. [The Python Package Index (PyPI)](https://pypi.org/) has a vast range of packages you can use in your own Python programs. Check out [Django Packages](https://djangopackages.org) for existing reusable apps you could incorporate in your project. Django itself is also a normal Python package. This means that you can take existing Python packages or Django apps and compose them into your own web project. You only need to write the parts that make your project unique.

Let’s say you were starting a new project that needed a polls app like the one we’ve been working on. How do you make this app reusable? Luckily, you’re well on the way already. In [Tutorial 1](../tutorial01/), we saw how we could decouple polls from the project-level URLconf using an `include`. In this tutorial, we’ll take further steps to make the app easy to use in new projects and ready to publish for others to install and use.

Package? App?

A Python [package](https://docs.python.org/3/glossary.html#term-package) provides a way of grouping related Python code for easy reuse. A package contains one or more files of Python code (also known as “modules”).

A package can be imported with `import foo.bar` or `from foo import bar`. For a directory (like `polls`) to form a package, it must contain a special file `__init__.py`, even if this file is empty.

A Django *application* is a Python package that is specifically intended for use in a Django project. An application may use common Django conventions, such as having `models`, `tests`, `urls`, and `views` submodules.

Later on we use the term *packaging* to describe the process of making a Python package easy for others to install. It can be a little confusing, we know.

## Your Project And Your Reusable App

After the previous tutorials, our project should look like this:

```
djangotutorial/
 manage.py
 mysite/
  __init__.py
  settings.py
  urls.py
  asgi.py
  wsgi.py
 polls/
  __init__.py
  admin.py
  apps.py
  migrations/
   __init__.py
   0001_initial.py
  models.py
  static/
   polls/
    images/
     background.png
    style.css
  templates/
   polls/
    detail.html
    index.html
    results.html
  tests.py
  urls.py
  views.py
 templates/
  admin/
   base_site.html
```

You created `djangotutorial/templates` in [Tutorial 7](../tutorial07/), and `polls/templates` in [Tutorial 3](../tutorial03/). Now perhaps it is clearer why we chose to have separate template directories for the project and application: everything that is part of the polls application is in `polls`. It makes the application self-contained and easier to drop into a new project.

The `polls` directory could now be copied into a new Django project and immediately reused. It’s not quite ready to be published though. For that, we need to package the app to make it easy for others to install.

## Installing Some Prerequisites

The current state of Python packaging is a bit muddled with various tools. For this tutorial, we’re going to use [setuptools](https://pypi.org/project/setuptools/) to build our package. It’s the recommended packaging tool (merged with the `distribute` fork). We’ll also be using [pip](https://pypi.org/project/pip/) to install and uninstall it. You should install these two packages now. If you need help, you can refer to [how to install Django with pip](../../topics/install/#installing-official-release). You can install `setuptools` the same way.

## Packaging Your App

Python *packaging* refers to preparing your app in a specific format that can be easily installed and used. Django itself is packaged very much like this. For a small app like polls, this process isn’t too difficult.

1.  First, create a parent directory for the package, outside of your Django project. Call this directory `django-polls`.

    Choosing a name for your app

    When choosing a name for your package, check PyPI to avoid naming conflicts with existing packages. We recommend using a `django-` prefix for package names, to identify your package as specific to Django, and a corresponding `django_` prefix for your module name. For example, the `django-ratelimit` package contains the `django_ratelimit` module.

    Application labels (that is, the final part of the dotted path to application packages) *must* be unique in [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS). Avoid using the same label as any of the Django [contrib packages](../../ref/contrib/), for example `auth`, `admin`, or `messages`.

2.  Move the `polls` directory into `django-polls` directory, and rename it to `django_polls`.

3.  Edit `django_polls/apps.py` so that [`name`](../../ref/applications/#django.apps.AppConfig.name) refers to the new module name and add [`label`](../../ref/applications/#django.apps.AppConfig.label) to give a short name for the app:

    ```python
    from django.apps import AppConfig

    class PollsConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "django_polls"
        label = "polls"
    ```

4.  Create a file `django-polls/README.rst` with the following contents:

    ```rst
    ============
    django-polls
    ============

    django-polls is a Django app to conduct web-based polls.
    For each question, visitors can choose between a fixed number of answers.

    Detailed documentation is in the "docs" directory.

    Quick start
    -----------

    1. Add "polls" to your INSTALLED_APPS setting like this::

       INSTALLED_APPS = [
            ...,
            "django_polls",
        ]

    2. Include the polls URLconf in your project urls.py like this::

       path("polls/", include("django_polls.urls")),

    3. Run ``python manage.py migrate`` to create the models.

    4. Start the development server and visit the admin to create a poll.

    5. Visit the ``/polls/`` URL to participate in the poll.
    ```

5.  Create a `django-polls/LICENSE` file. Choosing a license is beyond the scope of this tutorial, but suffice it to say that code released publicly without a license is *useless*. Django and many Django-compatible apps are distributed under the BSD license; however, you’re free to pick your own license. Just be aware that your licensing choice will affect who is able to use your code.

6.  Next we’ll create the `pyproject.toml` file which details how to build and install the app. A full explanation of this file is beyond the scope of this tutorial, but the [Python Packaging User Guide](https://packaging.python.org/guides/writing-pyproject-toml/) has a good explanation. Create the `django-polls/pyproject.toml` file with the following contents:

    ```toml
    [build-system]
    requires=["setuptools>=61.0"]
    build-backend="setuptools.build_meta"

    [project]
    name="django-polls"
    version="0.1"
    dependencies=[
        "django>=X.Y",  # Replace "X.Y" as appropriate
    ]
    description="A Django app to conduct web-based polls."
    readme="README.rst"
    requires-python=">= 3.10"
    authors=[
        {name="Your Name", email="yourname@example.com"},
    ]
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: X.Y",  # Replace "X.Y" as appropriate
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]

    [project.urls]
    Homepage="https://www.example.com/"
    ```

7.  Many common files and Python modules and packages are included in the package by default. To include additional files, we’ll need to create a `MANIFEST.in` file. To include the templates and static files, create a file `django-polls/MANIFEST.in` with the following contents:

    ```
    recursive-include django_polls/static *
    recursive-include django_polls/templates *
    ```

8.  It’s optional, but recommended, to include detailed documentation with your app. Create an empty directory `django-polls/docs` for future documentation.

    Note that the `docs` directory won’t be included in your package unless you add some files to it. Many Django apps also provide their documentation online through sites like [readthedocs.org](https://readthedocs.org).

    Many Python projects, including Django and Python itself, use [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html) to build their documentation. If you choose to use Sphinx you can link back to the Django documentation by configuring [Intersphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html#intersphinx) and including a value for Django in your project’s `intersphinx_mapping` value:

    ```python
    intersphinx_mapping = {
        # ...
        "django": (
            "https://docs.djangoproject.com/en/stable/",
            None,
        ),
    }
    ```

    With that in place, you can then cross-link to specific entries, in the same way as in the Django docs, such as “`:attr:`django.test.TransactionTestCase.databases``”.

9.  Check that the [build](https://pypi.org/project/build/) package is installed (`python -m pip install build`) and try building your package by running `python -m build` inside `django-polls`. This creates a directory called `dist` and builds your new package into source and binary formats, `django-polls-0.1.tar.gz` and `django_polls-0.1-py3-none-any.whl`.

For more information on packaging, see Python’s [Tutorial on Packaging and Distributing Projects](https://packaging.python.org/tutorials/packaging-projects/).

## Using Your Own Package

Since we moved the `polls` directory out of the project, it’s no longer working. We’ll now fix this by installing our new `django-polls` package.

Installing as a user library

The following steps install `django-polls` as a user library. Per-user installs have a lot of advantages over installing the package system-wide, such as being usable on systems where you don’t have administrator access as well as preventing the package from affecting system services and other users of the machine.

Note that per-user installations can still affect the behavior of system tools that run as that user, so using a virtual environment is a more robust solution (see below).

1.  To install the package, use pip (you already [installed it](#installing-reusable-apps-prerequisites), right?):

    ```
    python -m pip install --user django-polls/dist/django-polls-0.1.tar.gz
    ```

2.  Update `mysite/settings.py` to point to the new module name:

    ```python
    INSTALLED_APPS = [
        "django_polls.apps.PollsConfig",
        ...,
    ]
    ```

3.  Update `mysite/urls.py` to point to the new module name:

    ```python
    urlpatterns = [
        path("polls/", include("django_polls.urls")),
        ...,
    ]
    ```

4.  Run the development server to confirm the project continues to work.

## Publishing Your App

Now that we’ve packaged and tested `django-polls`, it’s ready to share with the world! If this wasn’t just an example, you could now:

*   Email the package to a friend.
*   Upload the package on your website.
*   Post the package on a public repository, such as [the Python Package Index (PyPI)](https://pypi.org/). [packaging.python.org](https://packaging.python.org) has [a good tutorial](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) for doing this.

## Installing Python Packages With A Virtual Environment

Earlier, we installed `django-polls` as a user library. This has some disadvantages:

*   Modifying the user libraries can affect other Python software on your system.
*   You won’t be able to run multiple versions of this package (or others with the same name).

Typically, these situations only arise once you’re maintaining several Django projects. When they do, the best solution is to use [venv](https://docs.python.org/3/tutorial/venv.html). This tool allows you to maintain multiple isolated Python environments, each with its own copy of the libraries and package namespace.