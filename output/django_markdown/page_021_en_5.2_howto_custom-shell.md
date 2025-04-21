# How to customize the `shell` command

The Django `shell` is an interactive Python environment that provides access to models and settings, making it useful for testing code, experimenting with queries, and interacting with application data.

Customizing the `shell` command allows adding extra functionality or pre-loading specific modules. To do this, create a new management command that subclasses `django.core.management.commands.shell.Command` and overrides the existing `shell` management command. For more details, refer to the guide on [overriding commands](../custom-management-commands/#overriding-commands).

## Customize automatic imports

*New in Django 5.2.*

To customize the automatic import behavior of the `shell` management command, override the `get_auto_imports()` method. This method should return a sequence of import paths for objects or modules available in the application. For example:

```python
from django.core.management.commands import shell

class Command(shell.Command):
    def get_auto_imports(self):
        return super().get_auto_imports() + [
            "django.urls.reverse",
            "django.urls.resolve",
        ]
```

The customization above adds `resolve()` and `reverse()` to the default namespace, which already includes all models from the apps listed in `INSTALLED_APPS`. These objects will be available in the `shell` without requiring a manual import.

Running this customized `shell` command with `verbosity=2` would show:

```
8 objects imported automatically:
 from django.contrib.admin.models import LogEntry
 from django.contrib.auth.models import Group, Permission, User
 from django.contrib.contenttypes.models import ContentType
 from django.contrib.sessions.models import Session
 from django.urls import resolve, reverse
```

If an overridden `shell` command includes paths that cannot be imported, these errors are shown when `verbosity` is set to `1` or higher. Duplicate imports are automatically handled.

Note that automatic imports can be disabled for a specific `shell` session using the `--no-imports` flag. To permanently disable automatic imports, override `get_auto_imports()` to return `None`:

```python
class Command(shell.Command):
    def get_auto_imports(self):
        return None
```