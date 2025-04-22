# Constraints Reference

The classes defined in this module create database constraints. They are added in the model `Meta.constraints` option.

## Referencing Built-in Constraints

Constraints are defined in `django.db.models.constraints`, but for convenience they’re imported into `django.db.models`. The standard convention is to use `from django.db import models` and refer to the constraints as `models.<Foo>Constraint`.

## Constraints in Abstract Base Classes

You must always specify a unique name for the constraint. As such, you cannot normally specify a constraint on an abstract base class, since the `Meta.constraints` option is inherited by subclasses, with exactly the same values for the attributes (including `name`) each time. To work around name collisions, part of the name may contain `'%(app_label)s'` and `'%(class)s'`, which are replaced, respectively, by the lowercased app label and class name of the concrete model. For example `CheckConstraint(condition=Q(age__gte=18), name='%(app_label)s_%(class)s_is_adult')`.

## Validation of Constraints

Constraints are checked during [model validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects).

## `BaseConstraint`

```python
class BaseConstraint(*name, violation_error_code=None, violation_error_message=None)
```

Base class for all constraints. Subclasses must implement `constraint_sql()`, `create_sql()`, `remove_sql()` and `validate()` methods.

**Deprecated since version 5.0:** Support for passing positional arguments is deprecated.

All constraints have the following parameters in common:

### `name`

```python
BaseConstraint.name
```

The name of the constraint. You must always specify a unique name for the constraint.

### `violation_error_code`

```python
BaseConstraint.violation_error_code
```

The error code used when `ValidationError` is raised during [model validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects). Defaults to `None`.

### `violation_error_message`

```python
BaseConstraint.violation_error_message
```

The error message used when `ValidationError` is raised during [model validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects). Defaults to `"Constraint “%(name)s” is violated."`.

### `validate()`

```python
BaseConstraint.validate(model, instance, exclude=None, using=DEFAULT_DB_ALIAS)
```

Validates that the constraint, defined on `model`, is respected on the `instance`. This will do a query on the database to ensure that the constraint is respected. If fields in the `exclude` list are needed to validate the constraint, the constraint is ignored.

Raise a `ValidationError` if the constraint is violated.

This method must be implemented by a subclass.

## `CheckConstraint`

```python
class CheckConstraint(*, condition, name, violation_error_code=None, violation_error_message=None)
```

Creates a check constraint in the database.

### `condition`

```python
CheckConstraint.condition
```

A `Q` object or boolean `Expression` that specifies the conditional check you want the constraint to enforce.

For example, `CheckConstraint(condition=Q(age__gte=18), name='age_gte_18')` ensures the age field is never less than 18.

#### Expression Order

`Q` argument order is not necessarily preserved, however the order of `Q` expressions themselves are preserved. This may be important for databases that preserve check constraint expression order for performance reasons. For example, use the following format if order matters:

```python
CheckConstraint(
    condition=Q(age__gte=18) & Q(expensive_check=condition),
    name="age_gte_18_and_others",
)
```

#### Oracle < 23c

Checks with nullable fields on Oracle < 23c must include a condition allowing for `NULL` values in order for `validate()` to behave the same as check constraints validation. For example, if `age` is a nullable field:

```python
CheckConstraint(
    condition=Q(age__gte=18) | Q(age__isnull=True),
    name="age_gte_18"
)
```

**Deprecated since version 5.1:** The `check` attribute is deprecated in favor of `condition`.

## `UniqueConstraint`

```python
class UniqueConstraint(*expressions, fields=(), name=None, condition=None, deferrable=None, include=None, opclasses=(), nulls_distinct=None, violation_error_code=None, violation_error_message=None)
```

Creates a unique constraint in the database.

### `expressions`

```python
UniqueConstraint.expressions
```

Positional argument `*expressions` allows creating functional unique constraints on expressions and database functions.

For example:

```python
UniqueConstraint(
    Lower("name").desc(),
    "category",
    name="unique_lower_name_category"
)
```

creates a unique constraint on the lowercased value of the `name` field in descending order and the `category` field in the default ascending order.

Functional unique constraints have the same database restrictions as `Index.expressions`.

### `fields`

```python
UniqueConstraint.fields
```

A list of field names that specifies the unique set of columns you want the constraint to enforce.

For example, `UniqueConstraint(fields=['room', 'date'], name='unique_booking')` ensures each room can only be booked once for each date.

### `condition`

```python
UniqueConstraint.condition
```

A `Q` object that specifies the condition you want the constraint to enforce.

For example:

```python
UniqueConstraint(
    fields=["user"],
    condition=Q(status="DRAFT"),
    name="unique_draft_user"
)
```

ensures that each user only has one draft.

These conditions have the same database restrictions as `Index.condition`.

### `deferrable`

```python
UniqueConstraint.deferrable
```

Set this parameter to create a deferrable unique constraint. Accepted values are `Deferrable.DEFERRED` or `Deferrable.IMMEDIATE`. For example:

```python
from django.db.models import Deferrable, UniqueConstraint
UniqueConstraint(
    name="unique_order",
    fields=["order"],
    deferrable=Deferrable.DEFERRED,
)
```

By default constraints are not deferred. A deferred constraint will not be enforced until the end of the transaction. An immediate constraint will be enforced immediately after every command.

#### MySQL, MariaDB, and SQLite

Deferrable unique constraints are ignored on MySQL, MariaDB, and SQLite as they do not support them.

**Warning**

Deferred unique constraints may lead to a [performance penalty](https://www.postgresql.org/docs/current/sql-createtable.html#id-1.9.3.85.9.4).

### `include`

```python
UniqueConstraint.include
```

A list or tuple of the names of the fields to be included in the covering unique index as non-key columns. This allows index-only scans to be used for queries that select only included fields (`include`) and filter only by unique fields (`fields`).

For example:

```python
UniqueConstraint(
    name="unique_booking",
    fields=["room", "date"],
    include=["full_name"]
)
```

will allow filtering on `room` and `date`, also selecting `full_name`, while fetching data only from the index.

Unique constraints with non-key columns are ignored for databases besides PostgreSQL.

Non-key columns have the same database restrictions as `Index.include`.

### `opclasses`

```python
UniqueConstraint.opclasses
```

The names of the [PostgreSQL operator classes](https://www.postgresql.org/docs/current/indexes-opclass.html) to use for this unique index. If you require a custom operator class, you must provide one for each field in the index.

For example:

```python
UniqueConstraint(
    name="unique_username",
    fields=["username"],
    opclasses=["varchar_pattern_ops"]
)
```

creates a unique index on `username` using `varchar_pattern_ops`.

`opclasses` are ignored for databases besides PostgreSQL.

### `nulls_distinct`

```python
UniqueConstraint.nulls_distinct
```

Whether rows containing `NULL` values covered by the unique constraint should be considered distinct from each other. The default value is `None` which uses the database default which is `True` on most backends.

For example:

```python
UniqueConstraint(
    name="ordering",
    fields=["ordering"],
    nulls_distinct=False
)
```

creates a unique constraint that only allows one row to store a `NULL` value in the `ordering` column.

Unique constraints with `nulls_distinct` are ignored for databases besides PostgreSQL 15+.

### `violation_error_code`

```python
UniqueConstraint.violation_error_code
```

The error code used when a `ValidationError` is raised during [model validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects).

Defaults to `BaseConstraint.violation_error_code`, when either `UniqueConstraint.condition` is set or `UniqueConstraint.fields` is not set.

If `UniqueConstraint.fields` is set without a `UniqueConstraint.condition`, defaults to the `Meta.unique_together` error code when there are multiple fields, and to the `Field.unique` error code when there is a single field.

**Changed in Django 5.2:** In older versions, the provided `UniqueConstraint.violation_error_code` was not used when `UniqueConstraint.fields` was set without a `UniqueConstraint.condition`.

### `violation_error_message`

```python
UniqueConstraint.violation_error_message
```

The error message used when a `ValidationError` is raised during [model validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects).

Defaults to `BaseConstraint.violation_error_message`, when either `UniqueConstraint.condition` is set or `UniqueConstraint.fields` is not set.

If `UniqueConstraint.fields` is set without a `UniqueConstraint.condition`, defaults to the `Meta.unique_together` error message when there are multiple fields, and to the `Field.unique` error message when there is a single field.

**Changed in Django 5.2:** In older versions, the provided `UniqueConstraint.violation_error_message` was not used when `UniqueConstraint.fields` was set without a `UniqueConstraint.condition`.