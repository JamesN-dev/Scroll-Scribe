# FAQ: Databases and Models

## How Can I See the Raw SQL Queries Django Is Running?

Make sure your Django `DEBUG` setting is set to `True`. Then do this:

```python
>>> from django.db import connection
>>> connection.queries
[{'sql': 'SELECT polls_polls.id, polls_polls.question, polls_polls.pub_date FROM polls_polls',
'time': '0.002'}]
```

`connection.queries` is only available if `DEBUG` is `True`. It’s a list of dictionaries in order of query execution. Each dictionary has the following:

- `sql` - The raw SQL statement
- `time` - How long the statement took to execute, in seconds.

`connection.queries` includes all SQL statements – INSERTs, UPDATES, SELECTs, etc. Each time your app hits the database, the query will be recorded.

If you are using [multiple databases](https://docs.djangoproject.com/en/5.2/topics/db/multi-db/), you can use the same interface on each member of the `connections` dictionary:

```python
>>> from django.db import connections
>>> connections["my_db_alias"].queries
```

If you need to clear the query list manually at any point in your functions, call `reset_queries()`, like this:

```python
from django.db import reset_queries
reset_queries()
```

## Can I Use Django With a Preexisting Database?

Yes. See [Integrating with a legacy database](https://docs.djangoproject.com/en/5.2/howto/legacy-databases/).

## If I Make Changes to a Model, How Do I Update the Database?

Take a look at Django’s support for [schema migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/#module-django.db.migrations).

If you don’t mind clearing data, your project’s `manage.py` utility has a `flush` option to reset the database to the state it was in immediately after `migrate` was executed.

## Do Django Models Support Multiple-Column Primary Keys?

No. Only single-column primary keys are supported.

But this isn’t an issue in practice, because there’s nothing stopping you from adding other constraints (using the `unique_together` model option or creating the constraint directly in your database), and enforcing the uniqueness at that level. Single-column primary keys are needed for things such as the admin interface to work; e.g., you need a single value to specify an object to edit or delete.

## Does Django Support NoSQL Databases?

NoSQL databases are not officially supported by Django itself. There are, however, a number of side projects and forks which allow NoSQL functionality in Django.

You can take a look on [the wiki page](https://code.djangoproject.com/wiki/NoSqlSupport) which discusses some projects.

## How Do I Add Database-Specific Options to My CREATE TABLE Statements, Such as Specifying MyISAM as the Table Type?

We try to avoid adding special cases in the Django code to accommodate all the database-specific options such as table type, etc. If you’d like to use any of these options, create a migration with a [RunSQL](https://docs.djangoproject.com/en/5.2/ref/migration-operations/#django.db.migrations.operations.RunSQL) operation that contains `ALTER TABLE` statements that do what you want to do.

For example, if you’re using MySQL and want your tables to use the MyISAM table type, use the following SQL:

```sql
ALTER TABLE myapp_mytable ENGINE=MyISAM;
```