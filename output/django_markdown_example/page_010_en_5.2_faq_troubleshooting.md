# Troubleshooting

This page contains some advice about errors and problems commonly encountered during the development of Django applications.

## Problems Running `django-admin`

### `command not found: django-admin`

[`django-admin`](https://docs.djangoproject.com/en/5.2/ref/django-admin/) should be on your system path if you installed Django via `pip`. If it’s not in your path, ensure you have your virtual environment activated and you can try running the equivalent command `python -m django`.

### macOS Permissions

If you’re using macOS, you may see the message “permission denied” when you try to run `django-admin`. This is because, on Unix-based systems like macOS, a file must be marked as “executable” before it can be run as a program. To do this, open Terminal.app and navigate (using the `cd` command) to the directory where [`django-admin`](https://docs.djangoproject.com/en/5.2/ref/django-admin/) is installed, then run the command `sudo chmod +x django-admin`.

## Miscellaneous

### I’m Getting a `UnicodeDecodeError`. What Am I Doing Wrong?

This class of errors happen when a bytestring containing non-ASCII sequences is transformed into a Unicode string and the specified encoding is incorrect. The output generally looks like this:

```
UnicodeDecodeError: 'ascii' codec can't decode byte 0x?? in position ?: ordinal not in range(128)
```

The resolution mostly depends on the context, however here are two common pitfalls producing this error:

- Your system locale may be a default ASCII locale, like the “C” locale on UNIX-like systems (can be checked by the `locale` command). If it’s the case, please refer to your system documentation to learn how you can change this to a UTF-8 locale.

**Related Resources:**

- [Unicode in Django](https://docs.djangoproject.com/en/5.2/ref/unicode/)
- [https://wiki.python.org/moin/UnicodeDecodeError](https://wiki.python.org/moin/UnicodeDecodeError)