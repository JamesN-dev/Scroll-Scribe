# FAQ: Using Django

## Why do I get an error about importing `DJANGO_SETTINGS_MODULE`?

Make sure that:

- The environment variable `DJANGO_SETTINGS_MODULE` is set to a fully-qualified Python module (i.e., `mysite.settings`).
- Said module is on `sys.path` (`import mysite.settings` should work).
- The module doesn’t contain syntax errors.

## I can’t stand your template language. Do I have to use it?

We happen to think our template engine is the best thing since chunky bacon, but we recognize that choosing a template language runs close to religion. There’s nothing about Django that requires using the template language, so if you’re attached to Jinja2, Mako, or whatever, feel free to use those.

## Do I have to use your model/database layer?

Nope. Just like the template system, the model/database layer is decoupled from the rest of the framework.

The one exception is: If you use a different database library, you won’t get to use Django’s automatically-generated admin site. That app is coupled to the Django database layer.

## How do I use image and file fields?

Using a `FileField` or an `ImageField` in a model takes a few steps:

1. In your settings file, you’ll need to define `MEDIA_ROOT` as the full path to a directory where you’d like Django to store uploaded files. (For performance, these files are not stored in the database.) Define `MEDIA_URL` as the base public URL of that directory. Make sure that this directory is writable by the web server’s user account.
2. Add the `FileField` or `ImageField` to your model, defining the `upload_to` option to specify a subdirectory of `MEDIA_ROOT` to use for uploaded files.
3. All that will be stored in your database is a path to the file (relative to `MEDIA_ROOT`). You’ll most likely want to use the convenience `url` attribute provided by Django. For example, if your `ImageField` is called `mug_shot`, you can get the absolute path to your image in a template with `{{ object.mug_shot.url }}`.

## How do I make a variable available to all my templates?

Sometimes your templates all need the same thing. A common example would be dynamically generated menus. At first glance, it seems logical to add a common dictionary to the template context.

The best way to do this in Django is to use a `RequestContext`. Details on how to do this are here: [Using RequestContext](https://docs.djangoproject.com/en/5.2/ref/templates/api/#subclassing-context-requestcontext).