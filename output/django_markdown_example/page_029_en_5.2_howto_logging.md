# How to configure and use logging

## Make a basic logging call

To send a log message from within your code, you place a logging call into it.

```python
import logging
logger = logging.getLogger(__name__)

def some_view(request):
    ...
    if some_risky_state:
        logger.warning("Platform is running at risk")
```

When this code is executed, a `LogRecord` containing that message will be sent to the logger. If you’re using Django’s default logging configuration, the message will appear in the console.

## Customize logging configuration

### Basic logging configuration

Create a `LOGGING` dictionary in your `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}
```

Configure a handler:

```python
LOGGING = {
    # ...
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'general.log',
        },
    },
}
```

Configure a logger mapping:

```python
LOGGING = {
    # ...
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['file'],
        },
    },
}
```

### Use logger namespacing

The hierarchical logger naming convention allows you to control which loggers get processed by which configurations. For example:

```python
logger = logging.getLogger('project.payment')
```

And configure:

```python
LOGGING = {
    # ...
    'loggers': {
        'project.payment': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False,
        },
    },
}
```

Propagation defaults to `True`. When set to `False`, log records from this logger won’t be handled by parent loggers.