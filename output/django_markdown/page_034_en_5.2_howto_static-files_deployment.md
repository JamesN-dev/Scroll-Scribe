# How to deploy static files

See also

For an introduction to the use of [`django.contrib.staticfiles`](../../../ref/contrib/staticfiles/#module-django.contrib.staticfiles "django.contrib.staticfiles: An app for handling static files."), see [How to manage static files (e.g. images, JavaScript, CSS)](../).

## Serving static files in production

The basic outline of putting static files into production consists of two steps: run the [`collectstatic`](../../../ref/contrib/staticfiles/#django-admin-collectstatic) command when static files change, then arrange for the collected static files directory ([`STATIC_ROOT`](../../../ref/settings/#std-setting-STATIC_ROOT)) to be moved to the static file server and served. Depending on the `staticfiles` [`STORAGES`](../../../ref/settings/#std-setting-STORAGES) alias, files may need to be moved to a new location manually or the [`post_process`](../../../ref/contrib/staticfiles/#django.contrib.staticfiles.storage.StaticFilesStorage.post_process "django.contrib.staticfiles.storage.StaticFilesStorage.post_process") method of the `Storage` class might take care of that.

As with all deployment tasks, the devil’s in the details. Every production setup will be a bit different, so you’ll need to adapt the basic outline to fit your needs. Below are a few common patterns that might help.

### Serving the site and your static files from the same server

If you want to serve your static files from the same server that’s already serving your site, the process may look something like:

*   Push your code up to the deployment server.
*   On the server, run [`collectstatic`](../../../ref/contrib/staticfiles/#django-admin-collectstatic) to copy all the static files into [`STATIC_ROOT`](../../../ref/settings/#std-setting-STATIC_ROOT).
*   Configure your web server to serve the files in [`STATIC_ROOT`](../../../ref/settings/#std-setting-STATIC_ROOT) under the URL [`STATIC_URL`](../../../ref/settings/#std-setting-STATIC_URL). For example, here’s [how to do this with Apache and mod_wsgi](../../deployment/wsgi/modwsgi/#serving-files).

You’ll probably want to automate this process, especially if you’ve got multiple web servers.

### Serving static files from a dedicated server

Most larger Django sites use a separate web server – i.e., one that’s not also running Django – for serving static files. This server often runs a different type of web server – faster but less full-featured. Some common choices are:

*   [Nginx](https://nginx.org/en/)
*   A stripped-down version of [Apache](https://httpd.apache.org/)

Configuring these servers is out of scope of this document; check each server’s respective documentation for instructions.

Since your static file server won’t be running Django, you’ll need to modify the deployment strategy to look something like:

*   When your static files change, run [`collectstatic`](../../../ref/contrib/staticfiles/#django-admin-collectstatic) locally.
*   Push your local [`STATIC_ROOT`](../../../ref/settings/#std-setting-STATIC_ROOT) up to the static file server into the directory that’s being served. [rsync](https://rsync.samba.org/) is a common choice for this step since it only needs to transfer the bits of static files that have changed.

### Serving static files from a cloud service or CDN

Another common tactic is to serve static files from a cloud storage provider like Amazon’s S3 and/or a CDN (content delivery network). This lets you ignore the problems of serving static files and can often make for faster-loading web pages (especially when using a CDN).

When using these services, the basic workflow would look a bit like the above, except that instead of using `rsync` to transfer your static files to the server you’d need to transfer the static files to the storage provider or CDN.

There’s any number of ways you might do this, but if the provider has an API, you can use a [custom file storage backend](../../custom-file-storage/) to integrate the CDN with your Django project. If you’ve written or are using a 3rd party custom storage backend, you can tell [`collectstatic`](../../../ref/contrib/staticfiles/#django-admin-collectstatic) to use it by setting `staticfiles` in [`STORAGES`](../../../ref/settings/#std-setting-STORAGES).

For example, if you’ve written an S3 storage backend in `myproject.storage.S3Storage` you could use it with:

```python
STORAGES = {
    # ...
    "staticfiles": {"BACKEND": "myproject.storage.S3Storage"}
}
```

Once that’s done, all you have to do is run [`collectstatic`](../../../ref/contrib/staticfiles/#django-admin-collectstatic) and your static files would be pushed through your storage package up to S3. If you later needed to switch to a different storage provider, you may only have to change `staticfiles` in the [`STORAGES`](../../../ref/settings/#std-setting-STORAGES) setting.

For details on how you’d write one of these backends, see [How to write a custom storage class](../../custom-file-storage/). There are 3rd party apps available that provide storage backends for many common file storage APIs. A good starting point is the [overview at djangopackages.org](https://djangopackages.org/grids/g/storage-backends/).

## Learn more

For complete details on all the settings, commands, template tags, and other pieces included in [`django.contrib.staticfiles`](../../../ref/contrib/staticfiles/#module-django.contrib.staticfiles "django.contrib.staticfiles: An app for handling static files."), see [the staticfiles reference](../../../ref/contrib/staticfiles/).