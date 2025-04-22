# How to Deploy Django

Django is full of shortcuts to make web developers' lives easier, but all those tools are of no use if you can't easily deploy your sites. Since Django's inception, ease of deployment has been a major goal.

There are many options for deploying your Django application, based on your architecture or your particular business needs, but that discussion is outside the scope of what Django can give you as guidance.

Django, being a web framework, needs a web server in order to operate. And since most web servers don't natively speak Python, we need an interface to make that communication happen. The `runserver` command starts a lightweight development server, which is not suitable for production.

Django currently supports two interfaces: WSGI and ASGI.

- [WSGI](https://wsgi.readthedocs.io/en/latest/) is the main Python standard for communicating between web servers and applications, but it only supports synchronous code.

- [ASGI](https://asgi.readthedocs.io/en/latest/) is the new, asynchronous-friendly standard that will allow your Django site to use asynchronous Python features, and asynchronous Django features as they are developed.

You should also consider how you will handle [static files](../static-files/deployment/) for your application, and how to handle [error reporting](../error-reporting/).

Finally, before you deploy your application to production, you should run through our [deployment checklist](checklist/) to ensure that your configurations are suitable.

## Deployment Options

### WSGI Deployment
- [How to deploy with WSGI](wsgi/)
  - [How to use Django with Gunicorn](wsgi/gunicorn/)
  - [How to use Django with uWSGI](wsgi/uwsgi/)
  - [How to use Django with Apache and `mod_wsgi`](wsgi/modwsgi/)
  - [How to authenticate against Django's user database from Apache](wsgi/apache-auth/)
  - [The `application` object](wsgi/#the-application-object)
  - [Configuring the settings module](wsgi/#configuring-the-settings-module)
  - [Applying WSGI middleware](wsgi/#applying-wsgi-middleware)

### ASGI Deployment
- [How to deploy with ASGI](asgi/)
  - [How to use Django with Daphne](asgi/daphne/)
  - [How to use Django with Hypercorn](asgi/hypercorn/)
  - [How to use Django with Uvicorn](asgi/uvicorn/)
  - [The `application` object](asgi/#the-application-object)
  - [Configuring the settings module](asgi/#configuring-the-settings-module)
  - [Applying ASGI middleware](asgi/#applying-asgi-middleware)

### Deployment Checklist
- [Deployment checklist](checklist/)
  - [Run `manage.py check --deploy`](checklist/#run-manage-py-check-deploy)
  - [Switch away from `manage.py runserver`](checklist/#switch-away-from-manage-py-runserver)
  - [Critical settings](checklist/#critical-settings)
  - [Environment-specific settings](checklist/#environment-specific-settings)
  - [HTTPS](checklist/#https)
  - [Performance optimizations](checklist/#performance-optimizations)
  - [Error reporting](checklist/#error-reporting)