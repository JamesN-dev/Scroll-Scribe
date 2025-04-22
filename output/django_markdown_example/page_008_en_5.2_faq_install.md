# FAQ: Installation

## How Do I Get Started?

1. [Download the code](https://www.djangoproject.com/download/).
2. Install Django (read the [installation guide](https://docs.djangoproject.com/en/5.2/intro/install/)).
3. Walk through the [tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/).
4. Check out the rest of the [documentation](https://docs.djangoproject.com/en/5.2/), and [ask questions](https://www.djangoproject.com/community/) if you run into trouble.

## What Are Django’s Prerequisites?

Django requires Python. See the table in the next question for the versions of Python that work with each version of Django. Other Python libraries may be required for some use cases, but you’ll receive an error about them as they’re needed.

For a development environment – if you just want to experiment with Django – you don’t need to have a separate web server installed or database server.

Django comes with its own [`lightweight development server`](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-runserver). For a production environment, Django follows the WSGI spec, [PEP 3333](https://peps.python.org/pep-3333/), which means it can run on a variety of web servers. See [Deploying Django](https://docs.djangoproject.com/en/5.2/howto/deployment/) for more information.

Django runs [SQLite](https://www.sqlite.org/) by default, which is included in Python installations. For a production environment, we recommend [PostgreSQL](https://www.postgresql.org/); but we also officially support [MariaDB](https://mariadb.org/), [MySQL](https://www.mysql.com/), [SQLite](https://www.sqlite.org/), and [Oracle](https://www.oracle.com/). See [Supported Databases](https://docs.djangoproject.com/en/5.2/ref/databases/) for more information.

## What Python Version Can I Use With Django?

| Django Version | Python Versions                                                                 |
|----------------|---------------------------------------------------------------------------------|
| 4.2            | 3.8, 3.9, 3.10, 3.11, 3.12 (added in 4.2.8)                                     |
| 5.0            | 3.10, 3.11, 3.12                                                               |
| 5.1            | 3.10, 3.11, 3.12, 3.13 (added in 5.1.3)                                         |
| 5.2            | 3.10, 3.11, 3.12, 3.13                                                         |

For each version of Python, only the latest micro release (A.B.C) is officially supported. You can find the latest micro version for each series on the [Python download page](https://www.python.org/downloads/).

We will support a Python version up to and including the first Django LTS release whose security support ends after security support for that version of Python ends. For example, Python 3.9 security support ends in October 2025 and Django 4.2 LTS security support ends in April 2026. Therefore Django 4.2 is the last version to support Python 3.9.

## What Python Version Should I Use With Django?

Since newer versions of Python are often faster, have more features, and are better supported, the latest version of Python 3 is recommended.

You don’t lose anything in Django by using an older release, but you don’t take advantage of the improvements and optimizations in newer Python releases. Third-party applications for use with Django are free to set their own version requirements.

## Should I Use the Stable Version or Development Version?

Generally, if you’re using code in production, you should be using a stable release. The Django project publishes a full stable release every eight months or so, with bugfix updates in between. These stable releases contain the API that is covered by our backwards compatibility guarantees; if you write code against stable releases, you shouldn’t have any problems upgrading when the next official version is released.