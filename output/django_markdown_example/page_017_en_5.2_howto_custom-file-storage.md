# How To Write A Custom Storage Class

If you need to provide custom file storage – a common example is storing files on some remote system – you can do so by defining a custom storage class. You’ll need to follow these steps:

1. Your custom storage system must be a subclass of `django.core.files.storage.Storage`:

```python
from django.core.files.storage import Storage

class MyStorage(Storage):
    ...
```

2. Django must be able to instantiate your storage system without any arguments. This means that any settings should be taken from `django.conf.settings`:

```python
from django.conf import settings
from django.core.files.storage import Storage

class MyStorage(Storage):
    def __init__(self, option=None):
        if not option:
            option = settings.CUSTOM_STORAGE_OPTIONS
        ...
```

3. Your storage class must implement the [`_open()`](#django.core.files.storage._open) and [`_save()`](#django.core.files.storage._save) methods, along with any other methods appropriate to your storage class. See below for more on these methods.

In addition, if your class provides local file storage, it must override the `path()` method.

4. Your storage class must be [deconstructible](https://docs.djangoproject.com/en/5.2/topics/migrations/#custom-deconstruct-method) so it can be serialized when it’s used on a field in a migration. As long as your field has arguments that are themselves [serializable](https://docs.djangoproject.com/en/5.2/topics/migrations/#migration-serializing), you can use the `django.utils.deconstruct.deconstructible` class decorator for this (that’s what Django uses on FileSystemStorage).

By default, the following methods raise `NotImplementedError` and will typically have to be overridden:

*   [`Storage.delete()`](https://docs.djangoproject.com/en/5.2/ref/files/storage/#django.core.files.storage.Storage.delete)
*   [`Storage.exists()`](https://docs.djangoproject.com/en/5.2/ref/files/storage/#django.core.files.storage.Storage.exists)
*   [`Storage.listdir()`](https://docs.djangoproject.com/en/5.2/ref/files/storage/#django.core.files.storage.Storage.listdir)
*   [`Storage.size()`](https://docs.djangoproject.com/en/5.2/ref/files/storage/#django.core.files.storage.Storage.size)
*   [`Storage.url()`](https://docs.djangoproject.com/en/5.2/ref/files/storage/#django.core.files.storage.Storage.url)

Note however that not all these methods are required and may be deliberately omitted. As it happens, it is possible to leave each method unimplemented and still have a working Storage.

By way of example, if listing the contents of certain storage backends turns out to be expensive, you might decide not to implement `Storage.listdir()`.

Another example would be a backend that only handles writing to files. In this case, you would not need to implement any of the above methods.

Ultimately, which of these methods are implemented is up to you. Leaving some methods unimplemented will result in a partial (possibly broken) interface.

You’ll also usually want to use hooks specifically designed for custom storage objects. These are:

`_open(name, mode='rb')`

**Required**.

Called by `Storage.open()`, this is the actual mechanism the storage class uses to open the file. This must return a `File` object, though in most cases, you’ll want to return some subclass here that implements logic specific to the backend storage system. The [`FileNotFoundError`](https://docs.python.org/3/library/exceptions.html#FileNotFoundError) exception should be raised when a file doesn’t exist.

`_save(name, content)`

Called by `Storage.save()`. The `name` will already have gone through `get_valid_name()` and `get_available_name()`, and the `content` will be a `File` object itself.

Should return the actual name of the file saved (usually the `name` passed in, but if the storage needs to change the file name return the new name instead).

`get_valid_name(name)`

Returns a filename suitable for use with the underlying storage system. The `name` argument passed to this method is either the original filename sent to the server or, if `upload_to` is a callable, the filename returned by that method after any path information is removed. Override this to customize how non-standard characters are converted to safe filenames.

The code provided on `Storage` retains only alpha-numeric characters, periods and underscores from the original filename, removing everything else.

`get_alternative_name(file_root, file_ext)`

Returns an alternative filename based on the `file_root` and `file_ext` parameters. By default, an underscore plus a random 7 character alphanumeric string is appended to the filename before the extension.

`get_available_name(name, max_length=None)`

Returns a filename that is available in the storage mechanism, possibly taking the provided filename into account. The `name` argument passed to this method will have already cleaned to a filename valid for the storage system, according to the `get_valid_name()` method described above.

The length of the filename will not exceed `max_length`, if provided. If a free unique filename cannot be found, a [`SuspiciousFileOperation`](https://docs.djangoproject.com/en/5.2/ref/exceptions/#django.core.exceptions.SuspiciousOperation) exception is raised.

If a file with `name` already exists, `get_alternative_name()` is called to obtain an alternative name.

## Use Your Custom Storage Engine

The first step to using your custom storage with Django is to tell Django about the file storage backend you’ll be using. This is done using the [`STORAGES`](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-STORAGES) setting. This setting maps storage aliases, which are a way to refer to a specific storage throughout Django, to a dictionary of settings for that specific storage backend. The settings in the inner dictionaries are described fully in the [`STORAGES`](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-STORAGES) documentation.

Storages are then accessed by alias from the [`django.core.files.storage.storages`](https://docs.djangoproject.com/en/5.2/ref/files/storage/#django.core.files.storage.storages) dictionary:

```python
from django.core.files.storage import storages

example_storage = storages["example"]
```