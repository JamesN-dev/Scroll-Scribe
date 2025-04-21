# How to integrate Django with a legacy database

While Django is best suited for developing new applications, it’s quite possible to integrate it into legacy databases. Django includes a couple of utilities to automate as much of this process as possible.

This document assumes you know the Django basics, as covered in the [tutorial](../../intro/tutorial01/).

Once you’ve got Django set up, you’ll follow this general process to integrate with an existing database.

## Give Django your database parameters

You’ll need to tell Django what your database connection parameters are, and what the name of the database is. Do that by editing the [DATABASES](../../ref/settings/#std-setting-DATABASES) setting and assigning values to the following keys for the `'default'` connection:

- [NAME](../../ref/settings/#std-setting-NAME)
- [ENGINE](../../ref/settings/#std-setting-DATABASE-ENGINE)
- [USER](../../ref/settings/#std-setting-USER)
- [PASSWORD](../../ref/settings/#std-setting-PASSWORD)
- [HOST](../../ref/settings/#std-setting-HOST)
- [PORT](../../ref/settings/#std-setting-PORT)

## Auto-generate the models

Django comes with a utility called [inspectdb](../../ref/django-admin/#django-admin-inspectdb) that can create models by introspecting an existing database. You can view the output by running this command:

```bash
$ python manage.py inspectdb
```

Save this as a file by using standard Unix output redirection:

```bash
$ python manage.py inspectdb > models.py
```

This feature is meant as a shortcut, not as definitive model generation. See the [documentation of inspectdb](../../ref/django-admin/#django-admin-inspectdb) for more information.

Once you’ve cleaned up your models, name the file `models.py` and put it in the Python package that holds your app. Then add the app to your [INSTALLED_APPS](../../ref/settings/#std-setting-INSTALLED_APPS) setting.

By default, [inspectdb](../../ref/django-admin/#django-admin-inspectdb) creates unmanaged models. That is, `managed = False` in the model’s [Meta](../../ref/models/options/#django.db.models.Options.Meta) class tells Django not to manage each table’s creation, modification, and deletion:

```python
class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=70)

    class Meta:
        managed = False
        db_table = "CENSUS_PERSONS"
```

If you do want to allow Django to manage the table’s lifecycle, you’ll need to change the [managed](../../ref/models/options/#django.db.models.Options.managed) option above to `True` (or remove it because `True` is its default value).

## Install the core Django tables

Next, run the [migrate](../../ref/django-admin/#django-admin-migrate) command to install any extra needed database records such as admin permissions and content types:

```bash
$ python manage.py migrate
```

## Test and tweak

Those are the basic steps – from here you’ll want to tweak the models Django generated until they work the way you’d like. Try accessing your data via the Django database API, and try editing objects via Django’s admin site, and edit the models file accordingly.