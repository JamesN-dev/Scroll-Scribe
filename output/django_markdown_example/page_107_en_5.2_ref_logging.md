# Logging

See also

- [How to configure and use logging](../../howto/logging/#logging-how-to)
- [Django logging overview](../../topics/logging/#logging-explanation)

Django’s logging module extends Python’s builtin `logging`.

Logging is configured as part of the general Django `django.setup()` function, so it’s always available unless explicitly disabled.

## Django’s default logging configuration

By default, Django uses Python’s `logging.config.dictConfig` format.

### Default logging conditions

The full set of default logging conditions are:

When `DEBUG` is `True`:

- The `django` logger sends messages in the `django` hierarchy (except `django.server`) at the `INFO` level or higher to the console.

When `DEBUG` is `False`:

- The `django` logger sends messages in the `django` hierarchy (except `django.server`) with `ERROR` or `CRITICAL` level to `AdminEmailHandler`.

Independently of the value of `DEBUG`:

- The `django.server` logger sends messages at the `INFO` level or higher to the console.

All loggers except `django.server` propagate logging to their parents, up to the root `django` logger. The `console` and `mail_admins` handlers are attached to the root logger to provide the behavior described above.

Python’s own defaults send records of level `WARNING` and higher to the console.

### Default logging definition

Django’s default logging configuration inherits Python’s defaults. It’s available as `django.utils.log.DEFAULT_LOGGING` and defined in [django/utils/log.py](https://github.com/django/django/blob/main/django/utils/log.py):

```python
{
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

See [Configuring logging](../../topics/logging/#configuring-logging) on how to complement or replace this default logging configuration.

## Django logging extensions

Django provides a number of utilities to handle the particular requirements of logging in a web server environment.

### Loggers

Django provides several built-in loggers.

#### `django`

The parent logger for messages in the `django` [named logger hierarchy](../../howto/logging/#naming-loggers-hierarchy). Django does not post messages using this name. Instead, it uses one of the loggers below.

#### `django.request`

Log messages related to the handling of requests. 5XX responses are raised as `ERROR` messages; 4XX responses are raised as `WARNING` messages. Requests that are logged to the `django.security` logger aren’t logged to `django.request`.

Messages to this logger have the following extra context:

- `status_code`: The HTTP response code associated with the request.
- `request`: The request object that generated the logging message.

#### `django.server`

Log messages related to the handling of requests received by the server invoked by the `runserver` command. HTTP 5XX responses are logged as `ERROR` messages, 4XX responses are logged as `WARNING` messages, and everything else is logged as `INFO`.

Messages to this logger have the following extra context:

- `status_code`: The HTTP response code associated with the request.
- `request`: The request object (a `socket.socket`) that generated the logging message.

#### `django.template`

Log messages related to the rendering of templates.

- Missing context variables are logged as `DEBUG` messages.

#### `django.db.backends`

Messages relating to the interaction of code with the database. For example, every application-level SQL statement executed by a request is logged at the `DEBUG` level to this logger.

Messages to this logger have the following extra context:

- `duration`: The time taken to execute the SQL statement.
- `sql`: The SQL statement that was executed.
- `params`: The parameters that were used in the SQL call.
- `alias`: The alias of the database used in the SQL call.

For performance reasons, SQL logging is only enabled when `settings.DEBUG` is set to `True`, regardless of the logging level or handlers that are installed.

This logging does not include framework-level initialization (e.g. `SET TIMEZONE`). Turn on query logging in your database if you wish to view all database queries.

#### `django.utils.autoreload`

Log messages related to automatic code reloading during the execution of the Django development server. This logger generates an `INFO` message upon detecting a modification in a source code file and may produce `WARNING` messages during filesystem inspection and event subscription processes.

#### `django.contrib.auth`

New in Django 4.2.16.

Log messages related to [django.contrib.auth](../contrib/auth/), particularly `ERROR` messages are generated when a `PasswordResetForm` is successfully submitted but the password reset email cannot be delivered due to a mail sending exception.

#### `django.contrib.gis`

Log messages related to [GeoDjango](../contrib/gis/) at various points: during the loading of external GeoSpatial libraries (GEOS, GDAL, etc.) and when reporting errors. Each `ERROR` log record includes the caught exception and relevant contextual data.

#### `django.dispatch`

This logger is used in [Signals](../signals/), specifically within the `Signal` class, to report issues when dispatching a signal to a connected receiver. The `ERROR` log record includes the caught exception as `exc_info` and adds the following extra context:

- `receiver`: The name of the receiver.
- `err`: The exception that occurred when calling the receiver.

#### `django.security.*`

The security loggers will receive messages on any occurrence of `SuspiciousOperation` and other security-related errors. There is a sub-logger for each subtype of security error, including all `SuspiciousOperation`s. The level of the log event depends on where the exception is handled. Most occurrences are logged as a warning, while any `SuspiciousOperation` that reaches the WSGI handler will be logged as an error. For example, when an HTTP `Host` header is included in a request from a client that does not match `ALLOWED_HOSTS`, Django will return a 400 response, and an error message will be logged to the `django.security.DisallowedHost` logger.

These log events will reach the `django` logger by default, which mails error events to admins when `DEBUG=False`. Requests resulting in a 400 response due to a `SuspiciousOperation` will not be logged to the `django.request` logger, but only to the `django.security` logger.

To silence a particular type of `SuspiciousOperation`, you can override that specific logger following this example:

```python
LOGGING = {
    # ...
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
    },
    # ...
}
```

Other `django.security` loggers not based on `SuspiciousOperation` are:

- `django.security.csrf`: For [CSRF failures](../../howto/csrf/#csrf-rejected-requests).

#### `django.db.backends.schema`

Logs the SQL queries that are executed during schema changes to the database by the [migrations framework](../../topics/migrations/). Note that it won’t log the queries executed by `RunPython`. Messages to this logger have `params` and `sql` in their extra context (but unlike `django.db.backends`, not duration). The values have the same meaning as explained in [django.db.backends](#django-db-logger).

#### `django.contrib.sessions`

Log messages related to the [session framework](../../topics/http/sessions/).

- Non-fatal errors occurring when using the `django.contrib.sessions.backends.cached_db.SessionStore` engine are logged as `ERROR` messages with the corresponding traceback.

### Handlers

Django provides one log handler in addition to [those provided by the Python logging module](https://docs.python.org/3/library/logging.handlers.html#module-logging.handlers).

#### `AdminEmailHandler`

This handler sends an email to the site `ADMINS` for each log message it receives.

If the log record contains a `request` attribute, the full details of the request will be included in the email. The email subject will include the phrase “internal IP” if the client’s IP address is in the `INTERNAL_IPS` setting; if not, it will include “EXTERNAL IP”.

If the log record contains stack trace information, that stack trace will be included in the email.

The `include_html` argument of `AdminEmailHandler` is used to control whether the traceback email includes an HTML attachment containing the full content of the debug web page that would have been produced if `DEBUG` were `True`. To set this value in your configuration, include it in the handler definition for `django.utils.log.AdminEmailHandler`, like this:

```python
"handlers": {
    "mail_admins": {
        "level": "ERROR",
        "class": "django.utils.log.AdminEmailHandler",
        "include_html": True,
    },
}
```

Be aware of the [security implications of logging](../../topics/logging/#logging-security-implications) when using the `AdminEmailHandler`.

By setting the `email_backend` argument of `AdminEmailHandler`, the [email backend](../../topics/email/#topic-email-backends) that is being used by the handler can be overridden, like this:

```python
"handlers": {
    "mail_admins": {
        "level": "ERROR",
        "class": "django.utils.log.AdminEmailHandler",
        "email_backend": "django.core.mail.backends.filebased.EmailBackend",
    },
}
```

By default, an instance of the email backend specified in `EMAIL_BACKEND` will be used.

The `reporter_class` argument of `AdminEmailHandler` allows providing an `django.views.debug.ExceptionReporter` subclass to customize the traceback text sent in the email body. You provide a string import path to the class you wish to use, like this:

```python
"handlers": {
    "mail_admins": {
        "level": "ERROR",
        "class": "django.utils.log.AdminEmailHandler",
        "include_html": True,
        "reporter_class": "somepackage.error_reporter.CustomErrorReporter",
    },
}
```

##### `send_mail`

Sends emails to admin users. To customize this behavior, you can subclass the `AdminEmailHandler` class and override this method.

### Filters

Django provides some log filters in addition to those provided by the Python logging module.

#### `CallbackFilter`

This filter accepts a callback function (which should accept a single argument, the record to be logged), and calls it for each record that passes through the filter. Handling of that record will not proceed if the callback returns False.

For instance, to filter out `UnreadablePostError` (raised when a user cancels an upload) from the admin emails, you would create a filter function:

```python
from django.http import UnreadablePostError

def skip_unreadable_post(record):
    if record.exc_info:
        exc_type, exc_value = record.exc_info[:2]
        if isinstance(exc_value, UnreadablePostError):
            return False
    return True
```

and then add it to your logging config:

```python
LOGGING = {
    # ...
    "filters": {
        "skip_unreadable_posts": {
            "()": "django.utils.log.CallbackFilter",
            "callback": skip_unreadable_post,
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["skip_unreadable_posts"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    # ...
}
```

#### `RequireDebugFalse`

This filter will only pass on records when settings.DEBUG is False.

This filter is used as follows in the default `LOGGING` configuration to ensure that the `AdminEmailHandler` only sends error emails to admins when `DEBUG` is `False`:

```python
LOGGING = {
    # ...
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    # ...
}
```

#### `RequireDebugTrue`

This filter is similar to `RequireDebugFalse`, except that records are passed only when `DEBUG` is `True`.