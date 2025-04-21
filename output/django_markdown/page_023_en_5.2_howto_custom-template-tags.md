# How to Create Custom Template Tags and Filters

## Code Layout

The most common place to specify custom template tags and filters is inside a Django app. If they relate to an existing app, it makes sense to bundle them there; otherwise, they can be added to a new app.

The app should contain a `templatetags` directory, at the same level as `models.py`, `views.py`, etc. If this doesn't already exist, create it - don't forget the `__init__.py` file to ensure the directory is treated as a Python package.

> **Note**: After adding the `templatetags` module, you will need to restart your server before you can use the tags or filters in templates.

Your custom tags and filters will live in a module inside the `templatetags` directory. The name of the module file is the name you'll use to load the tags later.

Example app layout:

```
polls/
    __init__.py
    models.py
    templatetags/
        __init__.py
        poll_extras.py
    views.py
```

In your template, you would use:

```django
{% load poll_extras %}
```

The app that contains the custom tags must be in `INSTALLED_APPS` in order for the `{% load %}` tag to work.

To be a valid tag library, the module must contain a module-level variable named `register` that is a `template.Library()` instance:

```python
from django import template
register = template.Library()
```

## Writing Custom Template Filters

Custom filters are Python functions that take one or two arguments:

- The value of the variable (input) – not necessarily a string
- The value of the argument – this can have a default value, or be left out altogether

Example filter definition:

```python
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, "")
```

Usage in template:

```django
{{ somevariable|cut:"0" }}
```

Most filters don't take arguments:

```python
def lower(value):
    """Converts a string into all lowercase"""
    return value.lower()
```

### Registering Custom Filters

Once you've written your filter, register it with your `Library` instance:

```python
register.filter("cut", cut)
register.filter("lower", lower)
```

You can also use it as a decorator:

```python
@register.filter(name="cut")
def cut(value, arg):
    return value.replace(arg, "")

@register.filter
def lower(value):
    return value.lower()
```

### Template Filters That Expect Strings

If you're writing a filter that only expects a string, use the `stringfilter` decorator:

```python
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def lower(value):
    return value.lower()
```

### Filters and Auto-escaping

When writing a custom filter, consider how it will interact with Django's auto-escaping behavior. There are two types of strings:

- **Raw strings**: Native Python strings that are escaped if auto-escaping is in effect
- **Safe strings**: Strings marked safe from further escaping

### Filters and Time Zones

For filters operating on datetime objects, register with `expects_localtime=True`:

```python
@register.filter(expects_localtime=True)
def businesshours(value):
    try:
        return 9 <= value.hour < 17
    except AttributeError:
        return ""
```

## Writing Custom Template Tags

### Simple Tags

Many template tags take arguments and return a result. Django provides the `simple_tag` helper:

```python
import datetime
from django import template

register = template.Library()

@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)
```

### Simple Block Tags

Block tags allow passing a section of rendered template into a custom tag:

```python
@register.simple_block_tag
def chart(content):
    return render_chart(source=content)
```

### Inclusion Tags

Inclusion tags display data by rendering another template:

```python
@register.inclusion_tag('results.html')
def show_results(poll):
    choices = poll.choice_set.all()
    return {"choices": choices}
```

## Advanced Custom Template Tags

For more complex scenarios, you can create template tags from scratch by defining compilation and rendering functions.

### Compilation Function

The compilation function converts a template tag into a `Node`:

```python
def do_current_time(parser, token):
    try:
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )
    return CurrentTimeNode(format_string[1:-1])
```

### Renderer

Define a `Node` subclass with a `render()` method:

```python
class CurrentTimeNode(template.Node):
    def __init__(self, format_string):
        self.format_string = format_string

    def render(self, context):
        return datetime.datetime.now().strftime(self.format_string)
```

## Thread-Safety Considerations

Ensure template tags are thread-safe by avoiding storing state on the node itself. Use the `render_context` for maintaining state specific to the current rendering.