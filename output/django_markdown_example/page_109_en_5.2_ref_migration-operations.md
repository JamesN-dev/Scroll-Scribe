# Migration Operations

Migration files are composed of one or more `Operation`s, objects that declaratively record what the migration should do to your database.

Django also uses these `Operation` objects to work out what your models looked like historically, and to calculate what changes you’ve made to your models since the last migration so it can automatically write your migrations; that’s why they’re declarative, as it means Django can easily load them all into memory and run through them without touching the database to work out what your project should look like.

There are also more specialized `Operation` objects which are for things like [data migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/#data-migrations) and for advanced manual database manipulation. You can also write your own `Operation` classes if you want to encapsulate a custom change you commonly make.

If you need an empty migration file to write your own `Operation` objects into, use `python manage.py makemigrations --empty yourappname`, but be aware that manually adding schema-altering operations can confuse the migration autodetector and make resulting runs of `makemigrations` output incorrect code.

All of the core Django operations are available from the `django.db.migrations.operations` module.

For introductory material, see the [migrations topic guide](https://docs.djangoproject.com/en/5.2/topics/migrations/).

## Schema Operations

### `CreateModel`

```python
class CreateModel(name, fields, options=None, bases=None, managers=None)
```

Creates a new model in the project history and a corresponding table in the database to match it.

- `name` is the model name, as would be written in the `models.py` file.
- `fields` is a list of 2-tuples of `(field_name, field_instance)`. The field instance should be an unbound field (so just `models.CharField(...)`, rather than a field taken from another model).
- `options` is an optional dictionary of values from the model’s `Meta` class.
- `bases` is an optional list of other classes to have this model inherit from; it can contain both class objects as well as strings in the format `"appname.ModelName"` if you want to depend on another model (so you inherit from the historical version). If it’s not supplied, it defaults to inheriting from the standard `models.Model`.
- `managers` takes a list of 2-tuples of `(manager_name, manager_instance)`. The first manager in the list will be the default manager for this model during migrations.

### `DeleteModel`

```python
class DeleteModel(name)
```

Deletes the model from the project history and its table from the database.

### `RenameModel`

```python
class RenameModel(old_name, new_name)
```

Renames the model from an old name to a new one.

You may have to manually add this if you change the model’s name and quite a few of its fields at once; to the autodetector, this will look like you deleted a model with the old name and added a new one with a different name, and the migration it creates will lose any data in the old table.

### `AlterModelTable`

```python
class AlterModelTable(name, table)
```

Changes the model’s table name (the `db_table` option on the `Meta` subclass).

### `AlterModelTableComment`

```python
class AlterModelTableComment(name, table_comment)
```

Changes the model’s table comment (the `db_table_comment` option on the `Meta` subclass).

### `AlterUniqueTogether`

```python
class AlterUniqueTogether(name, unique_together)
```

Changes the model’s set of unique constraints (the `unique_together` option on the `Meta` subclass).

### `AlterIndexTogether`

```python
class AlterIndexTogether(name, index_together)
```

Changes the model’s set of custom indexes (the `index_together` option on the `Meta` subclass).

**Warning**

`AlterIndexTogether` is officially supported only for pre-Django 4.2 migration files. For backward compatibility reasons, it’s still part of the public API, and there’s no plan to deprecate or remove it, but it should not be used for new migrations. Use `AddIndex` and `RemoveIndex` operations instead.

### `AlterOrderWithRespectTo`

```python
class AlterOrderWithRespectTo(name, order_with_respect_to)
```

Makes or deletes the `_order` column needed for the `order_with_respect_to` option on the `Meta` subclass.

### `AlterModelOptions`

```python
class AlterModelOptions(name, options)
```

Stores changes to miscellaneous model options (settings on a model’s `Meta`) like `permissions` and `verbose_name`. Does not affect the database, but persists these changes for `RunPython` instances to use. `options` should be a dictionary mapping option names to values.

### `AlterModelManagers`

```python
class AlterModelManagers(name, managers)
```

Alters the managers that are available during migrations.

### `AddField`

```python
class AddField(model_name, name, field, preserve_default=True)
```

Adds a field to a model. `model_name` is the model’s name, `name` is the field’s name, and `field` is an unbound Field instance (the thing you would put in the field declaration in `models.py` - for example, `models.IntegerField(null=True)`.

The `preserve_default` argument indicates whether the field’s default value is permanent and should be baked into the project state (`True`), or if it is temporary and just for this migration (`False`) - usually because the migration is adding a non-nullable field to a table and needs a default value to put into existing rows. It does not affect the behavior of setting defaults in the database directly - Django never sets database defaults and always applies them in the Django ORM code.

**Warning**

On older databases, adding a field with a default value may cause a full rewrite of the table. This happens even for nullable fields and may have a negative performance impact. To avoid that, the following steps should be taken.

1. Add the nullable field without the default value and run the `makemigrations` command. This should generate a migration with an `AddField` operation.
2. Add the default value to your field and run the `makemigrations` command. This should generate a migration with an `AlterField` operation.

### `RemoveField`

```python
class RemoveField(model_name, name)
```

Removes a field from a model.

Bear in mind that when reversed, this is actually adding a field to a model. The operation is reversible (apart from any data loss, which is irreversible) if the field is nullable or if it has a default value that can be used to populate the recreated column. If the field is not nullable and does not have a default value, the operation is irreversible.

**PostgreSQL**

`RemoveField` will also delete any additional database objects that are related to the removed field (like views, for example). This is because the resulting `DROP COLUMN` statement will include the `CASCADE` clause to ensure [dependent objects outside the table are also dropped](https://www.postgresql.org/docs/current/sql-altertable.html#SQL-ALTERTABLE-PARMS-CASCADE).

### `AlterField`

```python
class AlterField(model_name, name, field, preserve_default=True)
```

Alters a field’s definition, including changes to its type, `null`, `unique`, `db_column` and other field attributes.

The `preserve_default` argument indicates whether the field’s default value is permanent and should be baked into the project state (`True`), or if it is temporary and just for this migration (`False`) - usually because the migration is altering a nullable field to a non-nullable one and needs a default value to put into existing rows. It does not affect the behavior of setting defaults in the database directly - Django never sets database defaults and always applies them in the Django ORM code.

Note that not all changes are possible on all databases - for example, you cannot change a text-type field like `models.TextField()` into a number-type field like `models.IntegerField()` on most databases.

### `RenameField`

```python
class RenameField(model_name, old_name, new_name)
```

Changes a field’s name (and, unless `db_column` is set, its column name).

### `AddIndex`

```python
class AddIndex(model_name, index)
```

Creates an index in the database table for the model with `model_name`. `index` is an instance of the `Index` class.

### `RemoveIndex`

```python
class RemoveIndex(model_name, name)
```

Removes the index named `name` from the model with `model_name`.

### `RenameIndex`

```python
class RenameIndex(model_name, new_name, old_name=None, old_fields=None)
```

Renames an index in the database table for the model with `model_name`. Exactly one of `old_name` and `old_fields` can be provided. `old_fields` is an iterable of the strings, often corresponding to fields of `index_together` (pre-Django 5.1 option).

On databases that don’t support an index renaming statement (SQLite and MariaDB < 10.5.2), the operation will drop and recreate the index, which can be expensive.

### `AddConstraint`

```python
class AddConstraint(model_name, constraint)
```

Creates a [constraint](https://docs.djangoproject.com/en/5.2/models/constraints/) in the database table for the model with `model_name`.

### `RemoveConstraint`

```python
class RemoveConstraint(model_name, name)
```

Removes the constraint named `name` from the model with `model_name`.

### `AlterConstraint`

**New in Django 5.2.**

```python
class AlterConstraint(model_name, name, constraint)
```

Alters the constraint named `name` of the model with `model_name` with the new `constraint` without affecting the database.

## Special Operations

### `RunSQL`

```python
class RunSQL(sql, reverse_sql=None, state_operations=None, hints=None, elidable=False)
```

Allows running of arbitrary SQL on the database - useful for more advanced features of database backends that Django doesn’t support directly.

- `sql`, and `reverse_sql` if provided, should be strings of SQL to run on the database. On most database backends (all but PostgreSQL), Django will split the SQL into individual statements prior to executing them.

**Warning**

On PostgreSQL and SQLite, only use `BEGIN` or `COMMIT` in your SQL in [non-atomic migrations](https://docs.djangoproject.com/en/5.2/howto/writing-migrations/#non-atomic-migrations), to avoid breaking Django’s transaction state.

You can also pass a list of strings or 2-tuples. The latter is used for passing queries and parameters in the same way as [cursor.execute()](https://docs.djangoproject.com/en/5.2/topics/db/sql/#executing-custom-sql). These three operations are equivalent:

```python
migrations.RunSQL("INSERT INTO musician (name) VALUES ('Reinhardt');")
migrations.RunSQL([("INSERT INTO musician (name) VALUES ('Reinhardt');", None)])
migrations.RunSQL([("INSERT INTO musician (name) VALUES (%s);", ["Reinhardt"])])
```

If you want to include literal percent signs in the query, you have to double them if you are passing parameters.

The `reverse_sql` queries are executed when the migration is unapplied. They should undo what is done by the `sql` queries. For example, to undo the above insertion with a deletion:

```python
migrations.RunSQL(
    sql=[("INSERT INTO musician (name) VALUES (%s);", ["Reinhardt"])],
    reverse_sql=[("DELETE FROM musician where name=%s;", ["Reinhardt"])],
)
```

If `reverse_sql` is `None` (the default), the `RunSQL` operation is irreversible.

The `state_operations` argument allows you to supply operations that are equivalent to the SQL in terms of project state. For example, if you are manually creating a column, you should pass in a list containing an `AddField` operation here so that the autodetector still has an up-to-date state of the model. If you don’t, when you next run `makemigrations`, it won’t see any operation that adds that field and so will try to run it again. For example:

```python
migrations.RunSQL(
    "ALTER TABLE musician ADD COLUMN name varchar(255) NOT NULL;",
    state_operations=[
        migrations.AddField(
            "musician",
            "name",
            models.CharField(max_length=255),
        ),
    ],
)
```

The optional `hints` argument will be passed as `**hints` to the `allow_migrate()` method of database routers to assist them in making routing decisions. See [Hints](https://docs.djangoproject.com/en/5.2/topics/db/multi-db/#topics-db-multi-db-hints) for more details on database hints.

The optional `elidable` argument determines whether or not the operation will be removed (elided) when [squashing migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/#migration-squashing).

#### `RunSQL.noop`

Pass the `RunSQL.noop` attribute to `sql` or `reverse_sql` when you want the operation not to do anything in the given direction. This is especially useful in making the operation reversible.

### `RunPython`

```python
class RunPython(code, reverse_code=None, atomic=None, hints=None, elidable=False)
```

Runs custom Python code in a historical context. `code` (and `reverse_code` if supplied) should be callable objects that accept two arguments; the first is an instance of `django.apps.registry.Apps` containing historical models that match the operation’s place in the project history, and the second is an instance of `SchemaEditor`.

The `reverse_code` argument is called when unapplying migrations. This callable should undo what is done in the `code` callable so that the migration is reversible. If `reverse_code` is `None` (the default), the `RunPython` operation is irreversible.

The optional `hints` argument will be passed as `**hints` to the `allow_migrate()` method of database routers to assist them in making a routing decision. See [Hints](https://docs.djangoproject.com/en/5.2/topics/db/multi-db/#topics-db-multi-db-hints) for more details on database hints.

The optional `elidable` argument determines whether or not the operation will be removed (elided) when [squashing migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/#migration-squashing).

You are advised to write the code as a separate function above the `Migration` class in the migration file, and pass it to `RunPython`. Here’s an example of using `RunPython` to create some initial objects on a `Country` model:

```python
from django.db import migrations

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Country = apps.get_model("myapp", "Country")
    db_alias = schema_editor.connection.alias
    Country.objects.using(db_alias).bulk_create(
        [
            Country(name="USA", code="us"),
            Country(name="France", code="fr"),
        ]
    )

def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    Country = apps.get_model("myapp", "Country")
    db_alias = schema_editor.connection.alias
    Country.objects.using(db_alias).filter(name="USA", code="us").delete()
    Country.objects.using(db_alias).filter(name="France", code="fr").delete()

class Migration(migrations.Migration):
    dependencies = []
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
```

This is generally the operation you would use to create [data migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/#data-migrations), run custom data updates and alterations, and anything else you need access to an ORM and/or Python code for.

Much like `RunSQL`, ensure that if you change schema inside here you’re either doing it outside the scope of the Django model system (e.g. triggers) or that you use `SeparateDatabaseAndState` to add in operations that will reflect your changes to the model state - otherwise, the versioned ORM and the autodetector will stop working correctly.

By default, `RunPython` will run its contents inside a transaction on databases that do not support DDL transactions (for example, MySQL and Oracle). This should be safe, but may cause a crash if you attempt to use the `schema_editor` provided on these backends; in this case, pass `atomic=False` to the `RunPython` operation.

On databases that do support DDL transactions (SQLite and PostgreSQL), `RunPython` operations do not have any transactions automatically added besides the transactions created for each migration. Thus, on PostgreSQL, for example, you should avoid combining schema changes and `RunPython` operations in the same migration or you may hit errors like `OperationalError: cannot ALTER TABLE "mytable" because it has pending trigger events`.

If you have a different database and aren’t sure if it supports DDL transactions, check the `django.db.connection.features.can_rollback_ddl` attribute.

If the `RunPython` operation is part of a [non-atomic migration](https://docs.djangoproject.com/en/5.2/howto/writing-migrations/#non-atomic-migrations), the operation will only be executed in a transaction if `atomic=True` is passed to the `RunPython` operation.

**Warning**

`RunPython` does not magically alter the connection of the models for you; any model methods you call will go to the default database unless you give them the current database alias (available from `schema_editor.connection.alias`, where `schema_editor` is the second argument to your function).

#### `RunPython.noop`

Pass the `RunPython.noop` method to `code` or `reverse_code` when you want the operation not to do anything in the given direction. This is especially useful in making the operation reversible.

### `SeparateDatabaseAndState`

```python
class SeparateDatabaseAndState(database_operations=None, state_operations=None)
```

A highly specialized operation that lets you mix and match the database (schema-changing) and state (autodetector-powering) aspects of operations.

It accepts two lists of operations. When asked to apply state, it will use the `state_operations` list (this is a generalized version of `RunSQL`’s `state_operations` argument). When asked to apply changes to the database, it will use the `database_operations` list.

If the actual state of the database and Django’s view of the state get out of sync, this can break the migration framework, even leading to data loss. It’s worth exercising caution and checking your database and state operations carefully. You can use `sqlmigrate` and `dbshell` to check your database operations. You can use `makemigrations`, especially with `--dry-run`, to check your state operations.

For an example using `SeparateDatabaseAndState`, see [Changing a ManyToManyField to use a through model](https://docs.djangoproject.com/en/5.2/howto/writing-migrations/#changing-a-manytomanyfield-to-use-a-through-model).

## Operation Category

**New in Django 5.1.**

```python
class OperationCategory
```

Categories of migration operation used by the `makemigrations` command to display meaningful symbols.

- **ADDITION**: Symbol `+`
- **REMOVAL**: Symbol `-`
- **ALTERATION**: Symbol `~`
- **PYTHON**: Symbol `p`
- **SQL**: Symbol `s`
- **MIXED**: Symbol `?`

## Writing Your Own

Operations have a relatively simple API, and they’re designed so that you can easily write your own to supplement the built-in Django ones. The basic structure of an `Operation` looks like this:

```python
from django.db.migrations.operations.base import Operation

class MyCustomOperation(Operation):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = False

    # This categorizes the operation. The corresponding symbol will be
    # displayed by the makemigrations command.
    category = OperationCategory.ADDITION

    def __init__(self, arg1, arg2):
        # Operations are usually instantiated with arguments in migration
        # files. Store the values of them on self for later use.
        pass

    def state_forwards(self, app_label, state):
        # The Operation should take the 'state' parameter (an instance of
        # django.db.migrations.state.ProjectState) and mutate it to match
        # any schema changes that have occurred.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        pass

    def describe(self):
        # This is used to describe what the operation does.
        return "Custom Operation"

    @property
    def migration_name_fragment(self):
        # Optional. A filename part suitable for automatically naming a
        # migration containing this operation, or None if not applicable.
        return "custom_operation_%s_%s" % (self.arg1, self.arg2)
```

You can take this template and work from it, though we suggest looking at the built-in Django operations in `django.db.migrations.operations` - they cover a lot of the example usage of semi-internal aspects of the migration framework like `ProjectState` and the patterns used to get historical models, as well as `ModelState` and the patterns used to mutate historical models in `state_forwards()`.

Some things to note:

- You don’t need to learn too much about `ProjectState` to write migrations; just know that it has an `apps` property that gives access to an app registry (which you can then call `get_model` on).
- `database_forwards` and `database_backwards` both get two states passed to them; these represent the difference the `state_forwards` method would have applied, but are given to you for convenience and speed reasons.
- If you want to work with model classes or model instances from the `from_state` argument in `database_forwards()` or `database_backwards()`, you must render model states using the `clear_delayed_apps_cache()` method to make related models available:

```python
def database_forwards(self, app_label, schema_editor, from_state, to_state):
    # This operation should have access to all models. Ensure that all models are
    # reloaded in case any are delayed.
    from_state.clear_delayed_apps_cache()
    ...
```

- `to_state` in the `database_backwards` method is the *older* state; that is, the one that will be the current state once the migration has finished reversing.
- You might see implementations of `references_model` on the built-in operations; this is part of the autodetection code and does not matter for custom operations.

**Warning**

For performance reasons, the `Field` instances in `ModelState.fields` are reused across migrations. You must never change the attributes on these instances. If you need to mutate a field in `state_forwards()`, you must remove the old instance from `ModelState.fields` and add a new instance in its place. The same is true for the `Manager` instances in `ModelState.managers`.

As an example, let’s make an operation that loads PostgreSQL extensions (which contain some of PostgreSQL’s more exciting features). Since there’s no model state changes, all it does is run one command:

```python
from django.db.migrations.operations.base import Operation

class LoadExtension(Operation):
    reversible = True

    def __init__(self, name):
        self.name = name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS %s" % self.name)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("DROP EXTENSION %s" % self.name)

    def describe(self):
        return "Creates extension %s" % self.name

    @property
    def migration_name_fragment(self):
        return "create_extension_%s" % self.name
```