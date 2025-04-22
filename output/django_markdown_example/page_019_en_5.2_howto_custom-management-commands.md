# How to create custom `django-admin` commands

Applications can register their own actions with `manage.py`. For example, you might want to add a `manage.py` action for a Django app that you're distributing. In this document, we will be building a custom `closepoll` command for the `polls` application from the [tutorial](../../intro/tutorial01/).

To do this, add a `management/commands` directory to the application. Django will register a `manage.py` command for each Python module in that directory whose name doesn't begin with an underscore. For example:

```
polls/
    __init__.py
    models.py
    management/
        __init__.py
        commands/
            __init__.py
            _private.py
            closepoll.py
    tests.py
    views.py
```

In this example, the `closepoll` command will be made available to any project that includes the `polls` application in [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS).

The `_private.py` module will not be available as a management command.

The `closepoll.py` module has only one requirement – it must define a class `Command` that extends [`BaseCommand`](#django.core.management.BaseCommand) or one of its [subclasses](#ref-basecommand-subclasses).

> **Note**
> 
> Standalone scripts
> 
> Custom management commands are especially useful for running standalone scripts or for scripts that are periodically executed from the UNIX crontab or from Windows scheduled tasks control panel.

To implement the command, edit `polls/management/commands/closepoll.py` to look like this:

```python
from django.core.management.base import BaseCommand, CommandError
from polls.models import Question as Poll

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        for poll_id in options["poll_ids"]:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError(f'Poll "{poll_id}" does not exist')
            
            poll.opened = False
            poll.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully closed poll "{poll_id}"')
            )
```

> **Note**
> 
> When you are using management commands and wish to provide console output, you should write to `self.stdout` and `self.stderr`, instead of printing to `stdout` and `stderr` directly. By using these proxies, it becomes much easier to test your custom command. Note also that you don't need to end messages with a newline character, it will be added automatically, unless you specify the `ending` parameter:
> 
> ```python
> self.stdout.write("Unterminated line", ending="")
> ```

The new custom command can be called using `python manage.py closepoll <poll_ids>`.

The `handle()` method takes one or more `poll_ids` and sets `poll.opened` to `False` for each one. If the user referenced any nonexistent polls, a [`CommandError`](#django.core.management.CommandError) is raised. The `poll.opened` attribute does not exist in the [tutorial](../../intro/tutorial02/) and was added to `polls.models.Question` for this example.

## Accepting optional arguments

The same `closepoll` could be easily modified to delete a given poll instead of closing it by accepting additional command line options. These custom options can be added in the [`add_arguments()`](#django.core.management.BaseCommand.add_arguments) method like this:

```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("poll_ids", nargs="+", type=int)
        
        # Named (optional) arguments
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete poll instead of closing it",
        )

    def handle(self, *args, **options):
        # ...
        if options["delete"]:
            poll.delete()
        # ...
```

The option (`delete` in our example) is available in the options dict parameter of the handle method. See the [`argparse`](https://docs.python.org/3/library/argparse.html#module-argparse) Python documentation for more about `add_argument` usage.

In addition to being able to add custom command line options, all [management commands](../../ref/django-admin/) can accept some default options such as [`--verbosity`](../../ref/django-admin/#cmdoption-verbosity) and [`--traceback`](../../ref/django-admin/#cmdoption-traceback).

## Management commands and locales

By default, management commands are executed with the current active locale.

If, for some reason, your custom management command must run without an active locale (for example, to prevent translated content from being inserted into the database), deactivate translations using the `@no_translations` decorator on your [`handle()`](#django.core.management.BaseCommand.handle) method:

```python
from django.core.management.base import BaseCommand, no_translations

class Command(BaseCommand):
    ...
    @no_translations
    def handle(self, *args, **options):
        ...
```

Since translation deactivation requires access to configured settings, the decorator can't be used for commands that work without configured settings.

## Testing

Information on how to test custom management commands can be found in the [testing docs](../../topics/testing/tools/#topics-testing-management-commands).

## Overriding commands

Django registers the built-in commands and then searches for commands in [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS) in reverse. During the search, if a command name duplicates an already registered command, the newly discovered command overrides the first.

In other words, to override a command, the new command must have the same name and its app must be before the overridden command's app in [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS).

Management commands from third-party apps that have been unintentionally overridden can be made available under a new name by creating a new command in one of your project's apps (ordered before the third-party app in [`INSTALLED_APPS`](../../ref/settings/#std-setting-INSTALLED_APPS)) which imports the `Command` of the overridden command.