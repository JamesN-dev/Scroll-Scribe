# How to provide initial data for models

It’s sometimes useful to prepopulate your database with hard-coded data when you’re first setting up an app. You can provide initial data with migrations or fixtures.

## Provide initial data with migrations

To automatically load initial data for an app, create a [data migration](https://docs.djangoproject.com/en/5.2/topics/migrations/#data-migrations). Migrations are run when setting up the test database, so the data will be available there, subject to [some limitations](https://docs.djangoproject.com/en/5.2/topics/testing/overview/#test-case-serialized-rollback).

## Provide data with fixtures

You can also provide data using [fixtures](https://docs.djangoproject.com/en/5.2/topics/db/fixtures/#fixtures-explanation), however, this data isn’t loaded automatically, except if you use [TransactionTestCase.fixtures](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-loaddata).

A fixture is a collection of data that Django knows how to import into a database. The most straightforward way of creating a fixture if you’ve already got some data is to use the [manage.py dumpdata command](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-dumpdata). Or, you can write fixtures by hand; fixtures can be written as JSON, XML or YAML (with [PyYAML](https://pyyaml.org/) installed) documents. The [serialization documentation](https://docs.djangoproject.com/en/5.2/topics/serialization/) has more details about each of these supported [serialization formats](https://docs.djangoproject.com/en/5.2/topics/serialization/#serialization-formats).

As an example, though, here’s what a fixture for a `Person` model might look like in JSON:

```json
[
  {
    "model": "myapp.person",
    "pk": 1,
    "fields": {
      "first_name": "John",
      "last_name": "Lennon"
    }
  },
  {
    "model": "myapp.person",
    "pk": 2,
    "fields": {
      "first_name": "Paul",
      "last_name": "McCartney"
    }
  }
]
```

And here’s that same fixture as YAML:

```yaml
- model: myapp.person
  pk: 1
  fields:
    first_name: John
    last_name: Lennon
- model: myapp.person
  pk: 2
  fields:
    first_name: Paul
    last_name: McCartney
```

You’ll store this data in a `fixtures` directory inside your app.

You can load data by calling [manage.py loaddata](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-loaddata) `<fixturename>`, where `<fixturename>` is the name of the fixture file you’ve created. Each time you run [loaddata](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-loaddata), the data will be read from the fixture and reloaded into the database. Note this means that if you change one of the rows created by a fixture and then run [loaddata](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-loaddata) again, you’ll wipe out any changes you’ve made.

### Tell Django where to look for fixture files

By default, Django looks for fixtures in the `fixtures` directory inside each app, so the command `loaddata sample` will find the file `my_app/fixtures/sample.json`. This works with relative paths as well, so `loaddata my_app/sample` will find the file `my_app/fixtures/my_app/sample.json`.

Django also looks for fixtures in the list of directories provided in the [FIXTURE_DIRS](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-FIXTURE_DIRS) setting.

To completely prevent default search from happening, use an absolute path to specify the location of your fixture file, e.g. `loaddata /path/to/sample`.