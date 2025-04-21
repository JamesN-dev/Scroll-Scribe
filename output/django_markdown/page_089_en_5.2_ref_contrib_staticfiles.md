# The `Staticfiles` App

`django.contrib.staticfiles` collects static files from each of your applications (and any other places you specify) into a single location that can easily be served in production.

See also:

For an introduction to the static files app and some usage examples, see [How to manage static files (e.g. images, JavaScript, CSS)](../../../howto/static-files/). For guidelines on deploying static files, see [How to deploy static files](../../../howto/static-files/deployment/).

## Settings

See [staticfiles settings](../../settings/#settings-staticfiles) for details on the following settings:

*   [`STORAGES`](../../settings/#std-setting-STORAGES)
*   [`STATIC_ROOT`](../../settings/#std-setting-STATIC_ROOT)
*   [`STATIC_URL`](../../settings/#std-setting-STATIC_URL)
*   [`STATICFILES_DIRS`](../../settings/#std-setting-STATICFILES_DIRS)
*   [`STATICFILES_FINDERS`](../../settings/#std-setting-STATICFILES_FINDERS)

## Management Commands

`django.contrib.staticfiles` exposes three management commands.

### `Collectstatic`

Collects the static files into [`STATIC_ROOT`](../../settings/#std-setting-STATIC_ROOT).

Duplicate file names are by default resolved in a similar way to how template resolution works: the file that is first found in one of the specified locations will be used. If you’re confused, the [`findstatic`](#django-admin-findstatic) command can help show you which files are found.

On subsequent `collectstatic` runs (if `STATIC_ROOT` isn’t empty), files are copied only if they have a modified timestamp greater than the timestamp of the file in `STATIC_ROOT`. Therefore if you remove an application from [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS), it’s a good idea to use the [`collectstatic --clear`](#cmdoption-collectstatic-clear) option in order to remove stale static files.

Files are searched by using the [`enabled finders`](../../settings/#std-setting-STATICFILES_FINDERS). The default is to look in all locations defined in [`STATICFILES_DIRS`](../../settings/#std-setting-STATICFILES_DIRS) and in the `'static'` directory of apps specified by the [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) setting.

The [`collectstatic`](#django-admin-collectstatic) management command calls the [`post_process()`](#django.contrib.staticfiles.storage.StaticFilesStorage.post_process) method of the `staticfiles` storage backend from [`STORAGES`](../../settings/#std-setting-STORAGES) after each run and passes a list of paths that have been found by the management command. It also receives all command line options of [`collectstatic`](#django-admin-collectstatic). This is used by the [`ManifestStaticFilesStorage`](#django.contrib.staticfiles.storage.ManifestStaticFilesStorage) by default.

By default, collected files receive permissions from [`FILE_UPLOAD_PERMISSIONS`](../../settings/#std-setting-FILE_UPLOAD_PERMISSIONS) and collected directories receive permissions from [`FILE_UPLOAD_DIRECTORY_PERMISSIONS`](../../settings/#std-setting-FILE_UPLOAD_DIRECTORY_PERMISSIONS). If you would like different permissions for these files and/or directories, you can subclass either of the [static files storage classes](#staticfiles-storages) and specify the `file_permissions_mode` and/or `directory_permissions_mode` parameters, respectively. For example:

```python
from django.contrib.staticfiles import storage

class MyStaticFilesStorage(storage.StaticFilesStorage):
    def __init__(self, *args, **kwargs):
        kwargs["file_permissions_mode"] = 0o640
        kwargs["directory_permissions_mode"] = 0o760
        super().__init__(*args, **kwargs)
```

Then set the `staticfiles` storage backend in [`STORAGES`](../../settings/#std-setting-STORAGES) setting to `'path.to.MyStaticFilesStorage'`.

Some commonly used options are:

*   `--noinput`, `--no-input`: Do NOT prompt the user for input of any kind.
*   `--ignore PATTERN`, `-i PATTERN`: Ignore files, directories, or paths matching this glob-style pattern. Use multiple times to ignore more. When specifying a path, always use forward slashes, even on Windows.
*   `--dry-run`, `-n`: Do everything except modify the filesystem.
*   `--clear`, `-c`: Clear the existing files before trying to copy or link the original file.
*   `--link`, `-l`: Create a symbolic link to each file instead of copying.
*   `--no-post-process`: Don’t call the [`post_process()`](#django.contrib.staticfiles.storage.StaticFilesStorage.post_process) method of the configured `staticfiles` storage backend from [`STORAGES`](../../settings/#std-setting-STORAGES).
*   `--no-default-ignore`: Don’t ignore the common private glob-style patterns `'CVS'`, `'.*'` and `'*~'`.

For a full list of options, refer to the commands own help by running:

```shell
$ python manage.py collectstatic --help
```

#### Customizing The Ignored Pattern List

The default ignored pattern list, `['CVS', '.*', '*~']`, can be customized in a more persistent way than providing the `--ignore` command option at each `collectstatic` invocation. Provide a custom [`AppConfig`](../../applications/#django.apps.AppConfig) class, override the `ignore_patterns` attribute of this class and replace `'django.contrib.staticfiles'` with that class path in your [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) setting:

```python
from django.contrib.staticfiles.apps import StaticFilesConfig

class MyStaticFilesConfig(StaticFilesConfig):
    ignore_patterns = [...]  # your custom ignore list
```

### `Findstatic`

Searches for one or more relative paths with the enabled finders.

For example:

```shell
$ python manage.py findstatic css/base.css admin/js/core.js
Found 'css/base.css' here:
  /home/special.polls.com/core/static/css/base.css
  /home/polls.com/core/static/css/base.css
Found 'admin/js/core.js' here:
  /home/polls.com/src/django/contrib/admin/media/js/core.js
```

By default, all matching locations are found. To only return the first match for each relative path, use the `--first` option:

```shell
$ python manage.py findstatic css/base.css --first
Found 'css/base.css' here:
  /home/special.polls.com/core/static/css/base.css
```

This is a debugging aid; it’ll show you exactly which static file will be collected for a given path.

By setting the `--verbosity` flag to 0, you can suppress the extra output and just get the path names:

```shell
$ python manage.py findstatic css/base.css --verbosity 0
/home/special.polls.com/core/static/css/base.css
/home/polls.com/core/static/css/base.css
```

On the other hand, by setting the `--verbosity` flag to 2, you can get all the directories which were searched:

```shell
$ python manage.py findstatic css/base.css --verbosity 2
Found 'css/base.css' here:
  /home/special.polls.com/core/static/css/base.css
  /home/polls.com/core/static/css/base.css
Looking in the following locations:
  /home/special.polls.com/core/static
  /home/polls.com/core/static
  /some/other/path/static
```

### `Runserver`

Overrides the core [`runserver`](../../django-admin/#django-admin-runserver) command if the `staticfiles` app is [`installed`](../../settings/#std-setting-INSTALLED_APPS) and adds automatic serving of static files. File serving doesn’t run through [`MIDDLEWARE`](../../settings/#std-setting-MIDDLEWARE).

The command adds these options:

*   `--nostatic`: Use the `--nostatic` option to disable serving of static files with the staticfiles app entirely. This option is only available if the staticfiles app is in your project’s [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) setting.

    Example usage:

    ```shell
    $ django-admin runserver --nostatic
    ```

*   `--insecure`: Use the `--insecure` option to force serving of static files with the staticfiles app even if the [`DEBUG`](../../settings/#std-setting-DEBUG) setting is `False`. By using this you acknowledge the fact that it’s **grossly inefficient** and probably **insecure**. This is only intended for local development, should **never be used in production** and is only available if the staticfiles app is in your project’s [`INSTALLED_APPS`](../../settings/#std-setting-INSTALLED_APPS) setting.

    `--insecure` doesn’t work with [`ManifestStaticFilesStorage`](#django.contrib.staticfiles.storage.ManifestStaticFilesStorage).

    Example usage:

    ```shell
    $ django-admin runserver --insecure
    ```

## Storages

### `StaticfilesStorage`

A subclass of the [`FileSystemStorage`](../../files/storage/#django.core.files.storage.FileSystemStorage) storage backend that uses the [`STATIC_ROOT`](../../settings/#std-setting-STATIC_ROOT) setting as the base file system location and the [`STATIC_URL`](../../settings/#std-setting-STATIC_URL) setting respectively as the base URL.

If this method is defined on a storage, it’s called by the [`collectstatic`](#django-admin-collectstatic) management command after each run and gets passed the local storages and paths of found files as a dictionary, as well as the command line options. It yields tuples of three values: `original_path, processed_path, processed`. The path values are strings and `processed` is a boolean indicating whether or not the value was post-processed, or an exception if post-processing failed.

The [`ManifestStaticFilesStorage`](#django.contrib.staticfiles.storage.ManifestStaticFilesStorage) uses this behind the scenes to replace the paths with their hashed counterparts and update the cache appropriately.

### `ManifeststaticfilesStorage`

A subclass of the [`StaticFilesStorage`](#django.contrib.staticfiles.storage.StaticFilesStorage) storage backend which stores the file names it handles by appending the MD5 hash of the file’s content to the filename. For example, the file `css/styles.css` would also be saved as `css/styles.55e7cbb9ba48.css`.

The purpose of this storage is to keep serving the old files in case some pages still refer to those files, e.g. because they are cached by you or a 3rd party proxy server. Additionally, it’s very helpful if you want to apply [far future Expires headers](https://developer.yahoo.com/performance/rules.html#expires) to the deployed files to speed up the load time for subsequent page visits.

The storage backend automatically replaces the paths found in the saved files matching other saved files with the path of the cached copy (using the [`post_process()`](#django.contrib.staticfiles.storage.StaticFilesStorage.post_process) method). The regular expressions used to find those paths (`django.contrib.staticfiles.storage.HashedFilesMixin.patterns`) cover:

*   The [@import](https://www.w3.org/TR/CSS2/cascade.html#at-import) rule and [url()](https://www.w3.org/TR/CSS2/syndata.html#uri) statement of [Cascading Style Sheets](https://www.w3.org/Style/CSS/).
*   [Source map](https://firefox-source-docs.mozilla.org/devtools-user/debugger/how_to/use_a_source_map/) comments in CSS and JavaScript files.

Subclass `ManifestStaticFilesStorage` and set the `support_js_module_import_aggregation` attribute to `True`, if you want to use the experimental regular expressions to cover:

*   The [modules import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#importing_features_into_your_script) in JavaScript.
*   The [modules aggregation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#aggregating_modules) in JavaScript.

For example, the `'css/styles.css'` file with this content:

```css
@import url("../admin/css/base.css");
```

…would be replaced by calling the [`url()`](../../files/storage/#django.core.files.storage.Storage.url) method of the `ManifestStaticFilesStorage` storage backend, ultimately saving a `'css/styles.55e7cbb9ba48.css'` file with the following content:

```css
@import url("../admin/css/base.27e20196a850.css");
```

> Usage of the `integrity` HTML attribute with local files
>
> When using the optional `integrity` attribute within tags like `<script>` or `<link>`, its value should be calculated based on the files as they are served, not as stored in the filesystem. This is particularly important because depending on how static files are collected, their checksum may have changed (for example when using [`collectstatic`](#django-admin-collectstatic)). At the moment, there is no out-of-the-box tooling available for this.

You can change the location of the manifest file by using a custom `ManifestStaticFilesStorage` subclass that sets the `manifest_storage` argument. For example:

```python
from django.conf import settings
from django.contrib.staticfiles.storage import (
    ManifestStaticFilesStorage,
    StaticFilesStorage,
)

class MyManifestStaticFilesStorage(ManifestStaticFilesStorage):
    def __init__(self, *args, **kwargs):
        manifest_storage = StaticFilesStorage(location=settings.BASE_DIR)
        super().__init__(*args, manifest_storage=manifest_storage, **kwargs)
```

> References in comments
>
> `ManifestStaticFilesStorage` doesn’t ignore paths in statements that are commented out. This [may crash on the nonexistent paths](https://code.djangoproject.com/ticket/21080). You should check and eventually strip comments.

This attribute provides a single hash that changes whenever a file in the manifest changes. This can be useful to communicate to SPAs that the assets on the server have changed (due to a new deployment).

Since static files might reference other static files that need to have their paths replaced, multiple passes of replacing paths may be needed until the file hashes converge. To prevent an infinite loop due to hashes not converging (for example, if `'foo.css'` references `'bar.css'` which references `'foo.css'`) there is a maximum number of passes before post-processing is abandoned. In cases with a large number of references, a higher number of passes might be needed. Increase the maximum number of passes by subclassing `ManifestStaticFilesStorage` and setting the `max_post_process_passes` attribute. It defaults to 5.

To enable the `ManifestStaticFilesStorage` you have to make sure the following requirements are met:

*   the `staticfiles` storage backend in [`STORAGES`](../../settings/#std-setting-STORAGES) setting is set to `'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'`
*   the [`DEBUG`](../../settings/#std-setting-DEBUG) setting is set to `False`
*   you’ve collected all your static files by using the [`collectstatic`](#django-admin-collectstatic) management command

Since creating the MD5 hash can be a performance burden to your website during runtime, `staticfiles` will automatically store the mapping with hashed names for all processed files in a file called `staticfiles.json`. This happens once when you run the [`collectstatic`](#django-admin-collectstatic) management command.

If a file isn’t found in the `staticfiles.json` manifest at runtime, a `ValueError` is raised. This behavior can be disabled by subclassing `ManifestStaticFilesStorage` and setting the `manifest_strict` attribute to `False` – nonexistent paths will remain unchanged.

Due to the requirement of running [`collectstatic`](#django-admin-collectstatic), this storage typically shouldn’t be used when running tests as `collectstatic` isn’t run as part of the normal test setup. During testing, ensure that `staticfiles` storage backend in the [`STORAGES`](../../settings/#std-setting-STORAGES) setting is set to something else like `'django.contrib.staticfiles.storage.StaticFilesStorage'` (the default).

The method that is used when creating the hashed name of a file. Needs to return a hash for the given file name and content. By default it calculates a MD5 hash from the content’s chunks as mentioned above. Feel free to override this method to use your own hashing algorithm.

### `ManifestfilesMixin`

Use this mixin with a custom storage to append the MD5 hash of the file’s content to the filename as [`ManifestStaticFilesStorage`](#django.contrib.staticfiles.storage.ManifestStaticFilesStorage) does.

## Finders Module

`staticfiles` finders has a `searched_locations` attribute which is a list of directory paths in which the finders searched. Example usage:

```python
from django.contrib.staticfiles import finders

result = finders.find("css/base.css")
searched_locations = finders.searched_locations
```

## Other Helpers

There are a few other helpers outside of the `staticfiles` app to work with static files:

*   The [`django.template.context_processors.static()`](../../templates/api/#django.template.context_processors.static) context processor which adds [`STATIC_URL`](../../settings/#std-setting-STATIC_URL) to every template context rendered with [`RequestContext`](../../templates/api/#django.template.RequestContext) contexts.
*   The builtin template tag [`static`](../../templates/builtins/#std-templatetag-static) which takes a path and urljoins it with the static prefix [`STATIC_URL`](../../settings/#std-setting-STATIC_URL). If `django.contrib.staticfiles` is installed, the tag uses the `url()` method of the `staticfiles` storage backend from [`STORAGES`](../../settings/#std-setting-STORAGES) instead.
*   The builtin template tag [`get_static_prefix`](../../templates/builtins/#std-templatetag-get_static_prefix) which populates a template variable with the static prefix [`STATIC_URL`](../../settings/#std-setting-STATIC_URL) to be used as a variable or directly.
*   The similar template tag [`get_media_prefix`](../../templates/builtins/#std-templatetag-get_media_prefix) which works like [`get_static_prefix`](../../templates/builtins/#std-templatetag-get_static_prefix) but uses [`MEDIA_URL`](../../settings/#std-setting-MEDIA_URL).
*   The `staticfiles` key in [`django.core.files.storage.storages`](../../files/storage/#django.core.files.storage.storages) contains a ready-to-use instance of the staticfiles storage backend.

### Static File Development View

The static files tools are mostly designed to help with getting static files successfully deployed into production. This usually means a separate, dedicated static file server, which is a lot of overhead to mess with when developing locally. Thus, the `staticfiles` app ships with a **quick and dirty helper view** that you can use to serve files locally in development.

This view function serves static files in development.

> Warning
>
> This view will only work if [`DEBUG`](../../settings/#std-setting-DEBUG) is `True`.
>
> That’s because this view is **grossly inefficient** and probably **insecure**. This is only intended for local development, and should **never be used in production**.

> Note
>
> To guess the served files’ content types, this view relies on the [`mimetypes`](https://docs.python.org/3/library/mimetypes.html#module-mimetypes) module from the Python standard library, which itself relies on the underlying platform’s map files. If you find that this view doesn’t return proper content types for certain files, it is most likely that the platform’s map files are incorrect or need to be updated. This can be achieved, for example, by installing or updating the `mailcap` package on a Red Hat distribution, `mime-support` on a Debian distribution, or by editing the keys under `HKEY_CLASSES_ROOT` in the Windows registry.

This view is automatically enabled by [`runserver`](../../django-admin/#django-admin-runserver) (with a [`DEBUG`](../../settings/#std-setting-DEBUG) setting set to `True`). To use the view with a different local development server, add the following snippet to the end of your primary URL configuration:

```python
from django.conf import settings
from django.contrib.staticfiles import views
from django.urls import re_path

if settings.DEBUG:
    urlpatterns += [
        re_path(r"^static/(?P<path>.*)$", views.serve),
    ]
```

Note, the beginning of the pattern (`r'^static/'`) should be your [`STATIC_URL`](../../settings/#std-setting-STATIC_URL) setting.

Since this is a bit finicky, there’s also a helper function that’ll do this for you:

This will return the proper URL pattern for serving static files to your already defined pattern list. Use it like this:

```python
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# ... the rest of your URLconf here ...

urlpatterns += staticfiles_urlpatterns()
```

This will inspect your [`STATIC_URL`](../../settings/#std-setting-STATIC_URL) setting and wire up the view to serve static files accordingly. Don’t forget to set the [`STATICFILES_DIRS`](../../settings/#std-setting-STATICFILES_DIRS) setting appropriately to let `django.contrib.staticfiles` know where to look for files in addition to files in app directories.

> Warning
>
> This helper function will only work if [`DEBUG`](../../settings/#std-setting-DEBUG) is `True` and your [`STATIC_URL`](../../settings/#std-setting-STATIC_URL) setting is neither empty nor a full URL such as `http://static.example.com/`.
>
> That’s because this view is **grossly inefficient** and probably **insecure**. This is only intended for local development, and should **never be used in production**.

### Specialized Test Case To Support ‘Live Testing’

This unittest TestCase subclass extends [`django.test.LiveServerTestCase`](../../../topics/testing/tools/#django.test.LiveServerTestCase).

Just like its parent, you can use it to write tests that involve running the code under test and consuming it with testing tools through HTTP (e.g. Selenium, PhantomJS, etc.), because of which it’s needed that the static assets are also published.

But given the fact that it makes use of the [`django.contrib.staticfiles.views.serve()`](#django.contrib.staticfiles.views.serve) view described above, it can transparently overlay at test execution-time the assets provided by the `staticfiles` finders. This means you don’t need to run [`collectstatic`](#django-admin-collectstatic) before or as a part of your tests setup.